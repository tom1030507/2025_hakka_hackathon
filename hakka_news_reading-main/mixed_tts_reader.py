# ✅ 完整版 news_reading.py
import requests
from bs4 import BeautifulSoup
import re
from deep_translator import GoogleTranslator
import hakka_tts_module
from gtts import gTTS
from pydub import AudioSegment
import os

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

def split_smart_segments(text):
    def is_english_char(c):
        return c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    def is_punctuation(c):
        return c in " ，。'\",()0123456789:!?.（）、&「」"

    segments = []
    if not text:
        return segments

    current = text[0]
    is_eng = is_english_char(current)

    for c in text[1:]:
        if is_punctuation(c):
            current += c
        elif is_english_char(c) == is_eng:
            current += c
        else:
            segments.append(current)
            current = c
            is_eng = is_english_char(c)

    segments.append(current)
    return [seg for seg in segments if seg.strip()]  # 移除全是空白的段落


if __name__ == '__main__':
    clear_folder("temp_audio")
    os.makedirs("temp_audio", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    headers = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://www.ettoday.net/news/news-list.htm'
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    news_items = soup.select('div.part_list_2 a')
    news_url = None
    for a in news_items:
        href = a['href']
        if '/news/' in href and href.startswith('https://'):
            news_url = href
            break

    if not news_url:
        print("\u274c 找不到新聞連結")
        exit()

    res = requests.get(news_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.find('h1', class_='title').text.strip()
    time = soup.find('time').text.strip()
    content_div = soup.find('div', class_='story')
    paragraphs = content_div.find_all('p')

    # translator = GoogleTranslator(source='auto', target='zh-TW')
    translated_paragraphs = []
    translated_paragraphs.append(title)
    translated_paragraphs.append(time)

    for p in paragraphs:
        for strong in p.find_all('strong'):
            strong.extract()
        text = p.get_text(strip=True)
        if not text:
            continue

        # if re.search(r'[a-zA-Z]', text):
        #     try:
        #         translated = translator.translate(text)
        #         print(f"\U0001f310 翻譯原文：{text}\n➡️ 翻譯後：{translated}\n")
        #         text = translated
        #     except Exception:
        #         print("\u26a0\ufe0f 翻譯錯誤，保留原文：", text)

        translated_paragraphs.append(text)


    print(translated_paragraphs)
    # ====== 依語言生成語音段落 ======
    segments = []
    for idx, paragraph in enumerate(translated_paragraphs):
        subsegments = split_smart_segments(paragraph)
        for sub_idx, segment in enumerate(subsegments):
            seg_index = f"{idx}_{sub_idx}"
            if re.search(r'[a-zA-Z]', segment):
                try:
                    out_path = f"temp_audio/segment_{seg_index}.mp3"
                    tts = gTTS(text=segment, lang='en')
                    tts.save(out_path)
                    print(f"🟢 gTTS 成功 ({seg_index})")
                except Exception:
                    print(f"\u274c gTTS 錯誤，跳過段落 {seg_index}")
                    continue
            else:
                try:
                    out_path = f"temp_audio/segment_{seg_index}.wav"
                    hakka_tts_module.generate_hakka_wav(segment, seg_index)
                except Exception:
                    print(f"\u274c 客語 TTS 錯誤，跳過段落 {seg_index}")
                    continue
            segments.append(out_path)

    # ====== 合併語音段落 ======
    final_audio = AudioSegment.empty()
    pause = AudioSegment.silent(duration=500)
    for seg_path in segments:
        try:
            seg = AudioSegment.from_file(seg_path)
            final_audio += seg + pause
        except:
            continue

    final_audio.export(f"output/{title}.mp3", format="mp3")
    print("\u2705 合併完成，已輸出至 output/final_audio.mp3")
