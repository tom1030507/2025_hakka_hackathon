from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup
import re
import os
import random
from gtts import gTTS
from pydub import AudioSegment
import urllib.parse
from dotenv import load_dotenv # <-- 新增這一行
from datetime import timedelta
import hakka_tts_module
import json
import asyncio


# 在應用程式啟動時載入環境變數
load_dotenv() # <-- 新增這一行，通常放在應用程式的頂部

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static File Serving ---
# Create directories if they don't exist
os.makedirs("output", exist_ok=True)
os.makedirs("temp_audio", exist_ok=True)
# Mount 'output' directory to be accessible from '/output' URL path
app.mount("/output", StaticFiles(directory="output"), name="output")




@app.get("/api/news")
def get_news():
    try:
        # 1. Clear temp folders
        hakka_tts_module.clear_folder("temp_audio")

        # 2. Fetch news content
        headers = {'User-Agent': 'Mozilla/5.0'}
        list_url = 'https://www.ettoday.net/news/news-list.htm'
        res = requests.get(list_url, headers=headers, timeout=10, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        all_news_links = [a['href'] for a in soup.select('div.part_list_2 a') if '/news/' in a.get('href', '') and a['href'].startswith('https://')]
        
        if not all_news_links:
            raise HTTPException(status_code=404, detail="No news links found")

        # 隨機選擇一則新聞
        news_url = random.choice(all_news_links[:10])
        
        

        res = requests.get(news_url, headers=headers, timeout=10, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        title = soup.find('h1', class_='title').text.strip()
        time = soup.find('time').text.strip()
        content_div = soup.find('div', class_='story')
        paragraphs = content_div.find_all('p')
        # paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p') if p.get_text(strip=True)]
        
        news_content = []
        news_content.append(title)
        news_content.append(time)

        for p in paragraphs:
            for strong in p.find_all('strong'):
                strong.extract()
            for a in p.find_all('a'):
                a.extract()
            text = p.get_text(strip=True)
            if not text:
                continue
            news_content.append(text)
        # 儲存新聞內容（供後續生成使用）
        with open("temp_audio/news.json", "w", encoding="utf-8") as f:
            json.dump(news_content, f, ensure_ascii=False)

        return {"news": news_content}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {e}")
    except Exception as e:
        # Log the full error for debugging
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

        
def generate_english_mp3(text, out_path):
    """Wrapper for gTTS to run it in a thread."""
    try:
        gTTS(text=text, lang='en').save(out_path)
        print(f"🟢 gTTS 成功 ({os.path.basename(out_path)})")
    except Exception as e:
        print(f"❌ gTTS 失敗 ({os.path.basename(out_path)}): {e}")
        # In case of failure, create a silent file so the concatenation doesn't fail.
        AudioSegment.silent(duration=100).export(out_path, format="mp3")

@app.get("/api/audio")
async def get_audio():
    try:
        with open("temp_audio/news.json", "r", encoding="utf-8") as f:
            news_content = json.load(f)

        safe_title = re.sub(r'[\/*?:"<>|]', "", news_content[0])
        output_mp3name = f"{safe_title[:50]}.mp3"
        output_jsonname = f"{safe_title[:50]}.json"
        audio_url = f"output/{urllib.parse.quote(output_mp3name)}"
        json_url = f"output/{output_jsonname}"
        
        if os.path.exists(f"output/{output_mp3name}") and os.path.exists(json_url):
            print("memory")
            with open(json_url, "r", encoding="utf-8") as f:
                subtitle_blocks = json.load(f)
            audio_url = f"/output/{urllib.parse.quote(output_mp3name)}"
            return {
                "status": "memory",
                "audio_url": audio_url,
                "subtitles": subtitle_blocks
            }

        # --- Step 1: Setup Concurrency Control ---
        # Create a semaphore to limit concurrent Hakka TTS requests to avoid rate-limiting.
        CONCURRENT_LIMIT = 3
        semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

        # --- Helper function to process each segment with semaphore control ---
        async def process_segment(segment_func, *args):
            # This wrapper acquires the semaphore before running the blocking I/O task in a thread.
            async with semaphore:
                # Using asyncio.to_thread to run the blocking function without blocking the event loop.
                return await asyncio.to_thread(segment_func, *args)

        # --- Step 2: Create all TTS generation tasks ---
        tasks = []
        all_seg_paths = [] # To maintain order for later audio combination
        total_segments = sum(len(hakka_tts_module.split_smart_segments(p)) for p in news_content)
        print(f"總共要處理 {total_segments} 個語音片段...")

        for idx, paragraph in enumerate(news_content):
            subsegments = hakka_tts_module.split_smart_segments(paragraph)
            para_seg_paths = []
            all_seg_paths.append(para_seg_paths)

            for sub_idx, segment in enumerate(subsegments):
                seg_index = f"{idx}_{sub_idx}"
                task = None
                try:
                    # English segments (gTTS) are less likely to have strict rate limits,
                    # but we can run them through the semaphore as well for consistency.
                    if re.search(r'[a-zA-Z]', segment):
                        out_path = f"temp_audio/segment_{seg_index}.mp3"
                        # We use the same semaphore for gTTS to keep things simple.
                        task = process_segment(generate_english_mp3, segment, out_path)
                    # Hakka segments are the main reason for the semaphore.
                    else:
                        out_path = f"temp_audio/segment_{seg_index}.wav"
                        task = process_segment(hakka_tts_module.generate_hakka_wav, segment, seg_index)

                    para_seg_paths.append(out_path)
                    if task:
                        tasks.append(task)
                except Exception as e:
                    print(f"❌ 準備任務時發生錯誤 [{seg_index}]：{e}")

        # --- Step 3: Run all tasks concurrently (respecting the semaphore limit) ---
        print(f"▶️ 開始並行處理 {len(tasks)} 個語音生成任務 (並行上限: {CONCURRENT_LIMIT})...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for errors during execution
        failed_tasks = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Log the exception from the task
                print(f"❌ 任務 {i} 執行失敗: {result}")
                failed_tasks += 1
        
        if failed_tasks > 0:
            print(f"⚠️ {failed_tasks}/{len(tasks)} 個語音生成任務失敗。")
        else:
            print("✅ 所有語音生成任務已完成。")

        # --- Step 4: Combine audio segments and create subtitles ---
        final_audio = AudioSegment.empty()
        pause = AudioSegment.silent(duration=500)
        current_time = 0
        subtitle_blocks = []

        for idx, paragraph in enumerate(news_content):
            para_audio = AudioSegment.empty()
            seg_paths = all_seg_paths[idx]

            for path in seg_paths:
                try:
                    if os.path.exists(path) and os.path.getsize(path) > 0:
                        para_audio += AudioSegment.from_file(path)
                    else:
                        print(f"⚠️ 找不到或檔案為空，跳過: {path}")
                except Exception as e:
                    print(f"❌ 合併音檔失敗 {path}: {e}")

            start_ms = current_time
            end_ms = current_time + len(para_audio)
            subtitle_blocks.append({
                "index": idx + 1,
                "start": start_ms,
                "end": end_ms,
                "text": paragraph
            })
            
            final_audio += para_audio + pause
            current_time = end_ms + len(pause)

        # --- Step 4: Export final audio and subtitle data ---
        with open(json_url, "w", encoding="utf-8") as f:
            json.dump(subtitle_blocks, f, ensure_ascii=False)

        if len(final_audio) > 0:
            final_audio.export(f"output/{output_mp3name}", format="mp3")
            print(f"✅ 已輸出語音：output/{output_mp3name}")
            audio_url = f"/output/{urllib.parse.quote(output_mp3name)}"
        else:
            audio_url = None
            print("⚠️ 最終音檔為空，不進行匯出。")
        
        return {
            "status": "done",
            "audio_url": audio_url,
            "subtitles": subtitle_blocks
        }

    except Exception as e:
        # Log the full error for debugging
        print(f"An unexpected error occurred in get_audio: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/")
def read_root():
    return {"Hello": "World"}



# if __name__ == '__main__':
#     news = get_news()
#     result = get_audio()
#     print(result)