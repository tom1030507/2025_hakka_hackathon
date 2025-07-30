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
def get_news_and_audio():
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

        
@app.get("/api/audio")
def get_audio():
    try:
        with open("temp_audio/news.json", "r", encoding="utf-8") as f:
            news_content = json.load(f)
        # 3. Generate audio segments
        # 4. Combine audio segments

        final_audio = AudioSegment.empty()
        pause = AudioSegment.silent(duration=500)
        current_time = 0
        subtitle_blocks = []
        total = len(news_content)

        for idx, paragraph in enumerate(news_content):
            print(f"▶️ 正在處理第 {idx+1}/{total} 段（{(idx+1)/total:.1%}）...")

            subsegments = hakka_tts_module.split_smart_segments(paragraph)
            seg_paths = []

            for sub_idx, segment in enumerate(subsegments):
                seg_index = f"{idx}_{sub_idx}"
                try:
                    if re.search(r'[a-zA-Z]', segment):
                        out_path = f"temp_audio/segment_{seg_index}.mp3"
                        gTTS(text=segment, lang='en').save(out_path)
                        print(f"🟢 gTTS 成功 ({seg_index})")
                    else:
                        out_path = f"temp_audio/segment_{seg_index}.wav"
                        hakka_tts_module.generate_hakka_wav(segment, seg_index)
                    seg_paths.append(out_path)
                except Exception as e:
                    print(f"❌ 語音產生失敗 [{seg_index}]：{e}")

            # 合併整段段落的語音
            para_audio = AudioSegment.empty()
            for path in seg_paths:
                para_audio += AudioSegment.from_file(path)

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

        # ===== 匯出合併音檔與字幕 =====
        safe_title = re.sub(r'[\\/*?:"<>|]', '', news_content[0])
        final_audio.export(f"output/{safe_title}.mp3", format="mp3")
        print(f"✅ 已輸出語音：output/{safe_title}.mp3")

        with open(f"output/{safe_title}.srt", "w", encoding="utf-8") as f:
            for block in subtitle_blocks:
                f.write(f"{block['index']}\n")
                f.write(f"{hakka_tts_module.to_srt_time(block['start'])} --> {hakka_tts_module.to_srt_time(block['end'])}\n")
                f.write(f"{block['text']}\n\n")

        print(f"✅ 已輸出字幕：output/{safe_title}.srt")


        
        # 5. Export final audio and return data
        if len(final_audio) > 0:
            safe_title = re.sub(r'[\/*?:"<>|]', "", news_content[0])
            output_filename = f"{safe_title[:50]}.mp3"
            final_audio.export(f"output/{output_filename}", format="mp3")
            audio_url = f"/output/{urllib.parse.quote(output_filename)}"
        else:
            audio_url = None

        return {"audio_url": audio_url}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {e}")
    except Exception as e:
        # Log the full error for debugging
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/")
def read_root():
    return {"Hello": "World"}