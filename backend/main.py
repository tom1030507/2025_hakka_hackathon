from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup
import re
import os
from gtts import gTTS
from pydub import AudioSegment
import urllib.parse
from dotenv import load_dotenv # <- 新增這一行
from course_generator import CourseRequest, course_generator


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


# --- Helper Functions from hakka_news_reading-main ---

# Note: This is a placeholder for the Hakka TTS module.
# The credentials are not provided, so this part will fail gracefully.
class tts:
    def getToken(self, url, username, password):
        login_headers = {"Content-Type": "application/json; charset=utf-8"}
        login_account_data = {"username": username, "password": password}
        response = requests.post(f"{url}/api/v1/login", headers=login_headers, json=login_account_data, verify=False)
        response.raise_for_status()
        return "Bearer " + response.json()['token']

    def getTTSVideo(self, ttsUrl, token, scriptText):
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        payload = {
            "input": {"text": scriptText, "type": "common"},
            "voice": {"languageCode": "hak-xi-TW", "name": "hak-xi-TW-vs2-F01"},
            "audioConfig": {"speakingRate": 1}
        }
        return requests.post(f"{ttsUrl}/api/v1/tts/synthesize", headers=headers, json=payload, verify=False)

    def saveWaveFile(self, result, filename):
        with open(filename, 'wb') as f:
            f.write(result.content)

    def __init__(self, url, username, password, ttsUrl, filename, scriptText):
        # This will likely fail because credentials are empty.
        token = self.getToken(url, username, password)
        result = self.getTTSVideo(ttsUrl, token, scriptText)
        if result.status_code == 200:
            self.saveWaveFile(result, filename)
            print(f"🟢 客語 TTS 成功 ({filename})")
        else:
            print(f"❌ 客語 TTS 失敗 ({filename}): {result.status_code}")
            raise ConnectionError(f"Hakka TTS failed with status {result.status_code}")

def generate_hakka_wav(text, index):
    # 從環境變數中讀取憑證
    url = os.getenv("HAKKA_TTS_URL_BASE", "")
    ttsUrl = os.getenv("HAKKA_TTS_URL_TTS", "")
    username = os.getenv("HAKKA_TTS_USERNAME", "")
    password = os.getenv("HAKKA_TTS_PASSWORD", "")
    out_path = f"temp_audio/segment_{index}.wav"
    
    # 檢查憑證是否已設定
    if not all([url, ttsUrl, username, password]):
        print("警告：客語 TTS 憑證未設定，將跳過客語語音生成。")
        raise ValueError("Hakka TTS credentials are not set.") # 拋出錯誤讓外層捕獲

    tts(url, username, password, ttsUrl, out_path, text)

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

def split_smart_segments(text):
    def is_english_char(c): return c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    def is_punctuation(c): return c in " ，。'\",()0123456789:!?.（）、&「」"
    segments = []
    if not text: return segments
    current = text[0]
    is_eng = is_english_char(current)
    for c in text[1:]:
        if is_punctuation(c) or is_english_char(c) == is_eng:
            current += c
        else:
            segments.append(current)
            current = c
            is_eng = is_english_char(c)
    segments.append(current)
    return [seg for seg in segments if seg.strip()]

# --- API Endpoints ---

@app.get("/api/news_with_audio")
def get_news_and_audio():
    try:
        # 1. Clear temp folders
        clear_folder("temp_audio")

        # 2. Fetch news content
        headers = {'User-Agent': 'Mozilla/5.0'}
        list_url = 'https://www.ettoday.net/news/news-list.htm'
        res = requests.get(list_url, headers=headers, timeout=10, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        news_url = next(
            (a['href'] for a in soup.select('div.part_list_2 a') if '/news/' in a.get('href', '') and a['href'].startswith('https://')),
            None
        )
        if not news_url: raise HTTPException(status_code=404, detail="News link not found")

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
            text = p.get_text(strip=True)
            if not text:
                continue
            news_content.append(text)
        
        # news_content = [title] + paragraphs
        
        # 3. Generate audio segments
        audio_segments = []
        for i, p in enumerate(news_content):
            subsegments = split_smart_segments(p)
            for si, seg in enumerate(subsegments):
                seg_index = f"{i}_{si}"
                try:
                    if re.search(r'[a-zA-Z]', seg):
                        out_path = f"temp_audio/segment_{seg_index}.mp3"
                        gTTS(text=seg, lang='en').save(out_path)
                        print(f"🟢 gTTS 成功 ({seg_index})")
                    else:
                        # This will call the placeholder function and likely fail
                        out_path = f"temp_audio/segment_{seg_index}.wav"
                        generate_hakka_wav(seg, seg_index)
                    audio_segments.append(out_path)
                except Exception as e:
                    print(f"❌ 語音生成失敗，跳過片段 {seg_index}: {e}")
                    continue
        
        # 4. Combine audio segments
        final_audio = AudioSegment.empty()
        pause = AudioSegment.silent(duration=500)
        for seg_path in audio_segments:
            try:
                seg_audio = AudioSegment.from_file(seg_path)
                final_audio += seg_audio + pause
            except Exception as e:
                print(f"⚠️ 無法讀取音檔 {seg_path}, 跳過: {e}")
                continue
        
        # 5. Export final audio and return data
        if len(final_audio) > 0:
            safe_title = re.sub(r'[\/*?:"<>|]', "", title)
            output_filename = f"{safe_title[:50]}.mp3"
            final_audio.export(f"output/{output_filename}", format="mp3")
            audio_url = f"/output/{urllib.parse.quote(output_filename)}"
        else:
            audio_url = None

        return {"news": news_content, "audio_url": audio_url}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {e}")
    except Exception as e:
        # Log the full error for debugging
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/api/generate_course")
async def generate_course(request: CourseRequest):
    """
    生成課程內容的 API 端點
    
    Args:
        request: 包含 topic (主題), difficulty (難度), includeQuiz (是否包含測驗) 的請求
        
    Returns:
        課程數據列表
    """
    try:
        print(f"收到課程生成請求: topic={request.topic}, difficulty={request.difficulty}, includeQuiz={request.includeQuiz}")
        
        # 調用課程生成模組
        course_data = await course_generator.generate_course(request)
        
        print(f"課程生成完成，包含 {len(course_data)} 個章節")
        
        return {
            "success": True,
            "message": "課程生成成功",
            "data": course_data
        }
        
    except Exception as e:
        print(f"課程生成失敗: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"課程生成失敗: {str(e)}"
        )


@app.get("/")
def read_root():
    return {"Hello": "World"}
