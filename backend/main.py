from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re
import os
import random
from gtts import gTTS
from pydub import AudioSegment
import urllib.parse
from dotenv import load_dotenv
from datetime import timedelta
import hakka_tts_module
import hakka_trans_module
import json
import hashlib
import time
import asyncio

# Load environment variables at application startup
load_dotenv()

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
os.makedirs("temp_trans", exist_ok=True)
os.makedirs("tts_audio", exist_ok=True)

# Mount directories to be accessible from URL paths
app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/temp_audio", StaticFiles(directory="temp_audio"), name="temp_audio")
app.mount("/tts_audio", StaticFiles(directory="tts_audio"), name="tts_audio")

# --- Audio Cache Management ---
audio_cache = {}
AUDIO_CACHE_FILE = "tts_audio/audio_cache.json"

def load_audio_cache():
    """Load audio cache from file"""
    global audio_cache
    try:
        if os.path.exists(AUDIO_CACHE_FILE):
            with open(AUDIO_CACHE_FILE, 'r', encoding='utf-8') as f:
                audio_cache = json.load(f)
    except Exception as e:
        print(f"Error loading audio cache: {e}")

def save_audio_cache():
    """Save audio cache to file"""
    try:
        with open(AUDIO_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(audio_cache, f, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving audio cache: {e}")

def get_text_hash(text: str) -> str:
    """Generate a hash for the given text"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """Initialize directories and check service readiness"""
    try:
        # Ensure all directories exist
        for directory in ["output", "temp_audio", "temp_trans", "tts_audio"]:
            os.makedirs(directory, exist_ok=True)
        
        # Load audio cache
        load_audio_cache()
        
        # Check translation service health
        required_vars = ["HAKKA_TRANS_URL_BASE", "HAKKA_TRANS_URL_TRANS", "HAKKA_TRANS_USERNAME", "HAKKA_TRANS_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        
        # Warm up translation service (optional: add a test translation)
        try:
            hakka_trans_module.hakka_translate("測試", "test_init")
            print("Translation service warmed up successfully")
        except Exception as e:
            print(f"Translation service warmup failed: {e}")
            
    except Exception as e:
        print(f"Startup error: {e}")

# --- Pydantic Models for API Request/Response ---
class TranslationRequest(BaseModel):
    text: str
    index: str = "default"

class TranslationResponse(BaseModel):
    success: bool
    original_text: str
    translation_result: dict = None
    error_message: str = None
    file_path: str = None

class TTSRequest(BaseModel):
    text: str
    voice_type: str = "hakka"

class CourseTranslateRequest(BaseModel):
    text: str
    index: int

class CourseTranslateResponse(BaseModel):
    success: bool
    translatedText: str = None
    error_message: str = None

class TTSResponse(BaseModel):
    success: bool
    audio_url: str = None
    error_message: str = None
    file_path: str = None

@app.get("/api/news")
def get_news_and_audio():
    try:
        hakka_tts_module.clear_folder("temp_audio")
        headers = {'User-Agent': 'Mozilla/5.0'}
        list_url = 'https://www.ettoday.net/news/news-list.htm'
        res = requests.get(list_url, headers=headers, timeout=10, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        all_news_links = [a['href'] for a in soup.select('div.part_list_2 a') if '/news/' in a.get('href', '') and a['href'].startswith('https://')]
        
        if not all_news_links:
            raise HTTPException(status_code=404, detail="No news links found")

        news_url = random.choice(all_news_links[:10])
        res = requests.get(news_url, headers=headers, timeout=10, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        title = soup.find('h1', class_='title').text.strip()
        time = soup.find('time').text.strip()
        content_div = soup.find('div', class_='story')
        paragraphs = content_div.find_all('p')
        
        news_content = [title, time]
        for p in paragraphs:
            for strong in p.find_all('strong'):
                strong.extract()
            for a in p.find_all('a'):
                a.extract()
            text = p.get_text(strip=True)
            if text:
                news_content.append(text)
        
        with open("temp_audio/news.json", "w", encoding="utf-8") as f:
            json.dump(news_content, f, ensure_ascii=False)

        return {"news": news_content}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {e}")
    except Exception as e:
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

@app.post("/api/translate/course", response_model=CourseTranslateResponse)
async def translate_course_text(request: CourseTranslateRequest):
    """專為Course3.vue設計的翻譯API端點"""
    try:
        # 調用翻譯模組（新版本支持 Markdown 格式保留）
        translation_result = hakka_trans_module.hakka_translate(request.text, str(request.index))
        
        if translation_result and translation_result.get('success', False):
            # 提取翻譯後的文字（優先使用 translatedText，向後兼容 output）
            translated_text = translation_result.get('translatedText') or translation_result.get('output', '')
            if translated_text:
                return CourseTranslateResponse(
                    success=True,
                    translatedText=translated_text
                )
            else:
                return CourseTranslateResponse(
                    success=False,
                    error_message="翻譯結果為空"
                )
        else:
            error_msg = translation_result.get('error_message', '翻譯服務返回格式錯誤') if translation_result else '翻譯服務返回格式錯誤'
            return CourseTranslateResponse(
                success=False,
                error_message=error_msg
            )
            
    except RuntimeError as e:
        return CourseTranslateResponse(
            success=False,
            error_message=str(e)
        )
    except Exception as e:
        print(f"Course translation error: {e}")
        return CourseTranslateResponse(
            success=False,
            error_message=f"翻譯失敗: {str(e)}"
        )

@app.post("/api/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    try:
        hakka_tts_module.clear_folder("temp_trans")
        hakka_trans_module.hakka_translate(request.text, request.index)
        translation_file = f"temp_trans/translation_{request.index}.json"
        
        if os.path.exists(translation_file):
            with open(translation_file, 'r', encoding='utf-8') as f:
                translation_result = json.load(f)
            return TranslationResponse(
                success=True,
                original_text=request.text,
                translation_result=translation_result,
                file_path=translation_file
            )
        else:
            return TranslationResponse(
                success=False,
                original_text=request.text,
                error_message="Translation file not found after processing"
            )
    except RuntimeError as e:
        return TranslationResponse(
            success=False,
            original_text=request.text,
            error_message=str(e)
        )
    except Exception as e:
        print(f"Translation error: {e}")
        return TranslationResponse(
            success=False,
            original_text=request.text,
            error_message=f"Unexpected error: {str(e)}"
        )

@app.post("/api/translate/batch")
async def translate_batch_texts(texts: list[str]):
    results = []
    try:
        hakka_tts_module.clear_folder("temp_trans")
        for idx, text in enumerate(texts):
            index = f"batch_{idx}"
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    hakka_trans_module.hakka_translate(text, index)
                    translation_file = f"temp_trans/translation_{index}.json"
                    if os.path.exists(translation_file):
                        with open(translation_file, 'r', encoding='utf-8') as f:
                            translation_result = json.load(f)
                        results.append({
                            "success": True,
                            "original_text": text,
                            "translation_result": translation_result,
                            "index": index
                        })
                        break
                    else:
                        results.append({
                            "success": False,
                            "original_text": text,
                            "error_message": "Translation file not found",
                            "index": index
                        })
                        break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Retrying translation for text {index} (attempt {attempt + 1}): {e}")
                        await asyncio.sleep(retry_delay)
                        continue
                    results.append({
                        "success": False,
                        "original_text": text,
                        "error_message": str(e),
                        "index": index
                    })
        
        return {
            "total": len(texts),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }
    except Exception as e:
        print(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch translation error: {str(e)}")

@app.post("/api/tts", response_model=TTSResponse)
def generate_tts(request: TTSRequest):
    try:
        hakka_tts_module.clear_folder("temp_audio")
        if not request.text.strip():
            return TTSResponse(
                success=False,
                error_message="Text cannot be empty"
            )
        
        if request.voice_type != "hakka":
            return TTSResponse(
                success=False,
                error_message="Only 'hakka' voice type is supported"
            )
        
        text_hash = get_text_hash(request.text.strip())
        
        if text_hash in audio_cache:
            cached_audio = audio_cache[text_hash]
            if os.path.exists(cached_audio["file_path"]):
                audio_url = f"/tts_audio/{os.path.basename(cached_audio['file_path'])}"
                return TTSResponse(
                    success=True,
                    audio_url=audio_url,
                    file_path=cached_audio["file_path"]
                )
        
        safe_text = re.sub(r'[^\w\s-]', '', request.text.strip())
        safe_text = re.sub(r'[-\s]+', '_', safe_text)[:30]
        timestamp = str(int(time.time() * 1000))
        filename = f"tts_{safe_text}_{timestamp}"
        output_path = f"tts_audio/{filename}.wav"
        
        try:
            hakka_tts_module.generate_hakka_wav2(request.text, filename)
            temp_path = f"tts_audio/{filename}.wav"
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                os.rename(temp_path, output_path)
                audio_cache[text_hash] = {
                    "text": request.text.strip(),
                    "file_path": output_path,
                    "timestamp": int(time.time())
                }
                save_audio_cache()
                
                audio_url = f"/tts_audio/{filename}.wav"
                return TTSResponse(
                    success=True,
                    audio_url=audio_url,
                    file_path=output_path
                )
            else:
                return TTSResponse(
                    success=False,
                    error_message="Audio file was not created successfully or is empty"
                )
        except ValueError as e:
            return TTSResponse(
                success=False,
                error_message=f"Hakka TTS configuration error: {str(e)}"
            )
        except Exception as e:
            print(f"Hakka TTS error: {e}")
            return TTSResponse(
                success=False,
                error_message=f"Hakka TTS failed: {str(e)}"
            )
    except Exception as e:
        print(f"TTS generation error: {e}")
        return TTSResponse(
            success=False,
            error_message=f"TTS generation failed: {str(e)}"
        )

@app.get("/api/translate/files/{index}")
def get_translation_file(index: str):
    try:
        translation_file = f"temp_trans/translation_{index}.json"
        if os.path.exists(translation_file):
            with open(translation_file, 'r', encoding='utf-8') as f:
                translation_result = json.load(f)
            return translation_result
        else:
            raise HTTPException(status_code=404, detail="Translation file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading translation file: {str(e)}")

@app.delete("/api/translate/files")
def clear_translation_files():
    try:
        hakka_tts_module.clear_folder("temp_trans")
        return {"message": "Translation files cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing files: {str(e)}")

@app.get("/")
def read_root():
    return {"Hello": "World", "translation_api": "available", "tts_api": "available (Hakka only)"}