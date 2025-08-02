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

@app.get("/api/audio")
def get_audio():
    try:
        with open("temp_audio/news.json", "r", encoding="utf-8") as f:
            news_content = json.load(f)
        
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
                text_hash = get_text_hash(segment)
                
                if text_hash in audio_cache:
                    seg_path = audio_cache[text_hash]["file_path"]
                    if os.path.exists(seg_path):
                        seg_paths.append(seg_path)
                        print(f"🟢 Using cached audio ({seg_index})")
                        continue
                
                try:
                    if re.search(r'[a-zA-Z]', segment):
                        out_path = f"temp_audio/segment_{seg_index}.mp3"
                        gTTS(text=segment, lang='en').save(out_path)
                        print(f"🟢 gTTS 成功 ({seg_index})")
                    else:
                        out_path = f"temp_audio/segment_{seg_index}.wav"
                        hakka_tts_module.generate_hakka_wav(segment, seg_index)
                    
                    seg_paths.append(out_path)
                    audio_cache[text_hash] = {
                        "text": segment,
                        "file_path": out_path,
                        "timestamp": int(time.time())
                    }
                    save_audio_cache()
                except Exception as e:
                    print(f"❌ 語音產生失敗 [{seg_index}]：{e}")

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

        safe_title = re.sub(r'[\\/*?:"<>|]', '', news_content[0])
        final_audio.export(f"output/{safe_title}.mp3", format="mp3")
        print(f"✅ 已輸出語音：output/{safe_title}.mp3")

        with open(f"output/{safe_title}.srt", "w", encoding="utf-8") as f:
            for block in subtitle_blocks:
                f.write(f"{block['index']}\n")
                f.write(f"{hakka_tts_module.to_srt_time(block['start'])} --> {hakka_tts_module.to_srt_time(block['end'])}\n")
                f.write(f"{block['text']}\n\n")

        print(f"✅ 已輸出字幕：output/{safe_title}.srt")

        output_filename = f"{safe_title[:50]}.mp3"
        final_audio.export(f"output/{output_filename}", format="mp3")
        audio_url = f"/output/{urllib.parse.quote(output_filename)}" if len(final_audio) > 0 else None

        return {"audio_url": audio_url}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

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
        # Check translation service health
        health_check = await check_translation_service()
        if health_check["status"] != "ok":
            raise HTTPException(status_code=503, detail=f"Translation service not ready: {health_check['message']}")
        
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
            hakka_tts_module.generate_hakka_wav(request.text, filename)
            temp_path = f"temp_audio/segment_{filename}.wav"
            
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

@app.delete("/api/tts/cleanup")
def cleanup_tts_files():
    """
    Clean up all audio files in temp_audio folder
    """
    try:
        hakka_tts_module.clear_folder("tts_audio")
        hakka_tts_module.clear_folder("temp_audio")
        return {"message": "Temporary audio files cleaned up successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@app.get("/api/tts/health")
def check_tts_service():
    try:
        dirs_exist = all(os.path.exists(d) for d in ["tts_audio", "temp_audio"])
        hakka_available = hasattr(hakka_tts_module, 'generate_hakka_wav')
        url = os.getenv("HAKKA_TTS_URL_BASE", "")
        ttsUrl = os.getenv("HAKKA_TTS_URL_TTS", "")
        username = os.getenv("HAKKA_TTS_USERNAME", "")
        password = os.getenv("HAKKA_TTS_PASSWORD", "")
        credentials_configured = all([url, ttsUrl, username, password])
        
        status = "ok" if dirs_exist and hakka_available and credentials_configured else "error"
        
        return {
            "status": status,
            "directories_exist": dirs_exist,
            "hakka_tts_available": hakka_available,
            "credentials_configured": credentials_configured,
            "message": "TTS service is ready" if status == "ok" else "TTS service has configuration issues"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"TTS health check failed: {str(e)}"
        }

@app.get("/api/translate/health")
async def check_translation_service():
    try:
        required_vars = ["HAKKA_TRANS_URL_BASE", "HAKKA_TRANS_URL_TRANS", "HAKKA_TRANS_USERNAME", "HAKKA_TRANS_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return {
                "status": "error",
                "message": f"Missing environment variables: {', '.join(missing_vars)}"
            }
        
        # Test translation service
        try:
            hakka_trans_module.hakka_translate("健康檢查", "health_check")
            translation_file = f"temp_trans/translation_health_check.json"
            if os.path.exists(translation_file):
                return {
                    "status": "ok",
                    "message": "Translation service is properly configured and responsive"
                }
            else:
                return {
                    "status": "error",
                    "message": "Translation service failed to produce output file"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Translation service test failed: {str(e)}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }

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