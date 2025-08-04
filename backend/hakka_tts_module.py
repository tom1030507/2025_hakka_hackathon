import requests
from bs4 import BeautifulSoup
import re
import os
from gtts import gTTS
from pydub import AudioSegment
import urllib.parse
from dotenv import load_dotenv # <-- 新增這一行
from datetime import timedelta

# 在應用程式啟動時載入環境變數
load_dotenv() # <-- 新增這一行，通常放在應用程式的頂部

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


def generate_hakka_wav2(text, index):
    # 從環境變數中讀取憑證
    url = os.getenv("HAKKA_TTS_URL_BASE", "")
    ttsUrl = os.getenv("HAKKA_TTS_URL_TTS", "")
    username = os.getenv("HAKKA_TTS_USERNAME", "")
    password = os.getenv("HAKKA_TTS_PASSWORD", "")
    out_path = f"tts_audio/{index}.wav"
    
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
    def is_english_char(c): return c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
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

def to_srt_time(ms):
    t = timedelta(milliseconds=ms)
    return str(t)[:-3].replace('.', ',').rjust(12, '0')

# --- API Endpoints ---