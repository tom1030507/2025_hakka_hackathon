# 🎓 智能客家語學習平台 - 2025 客家黑客松專案

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Docker](https://img.shields.io/badge/docker-supported-blue.svg) ![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-red.svg) ![n8n](https://img.shields.io/badge/n8n-workflow-orange.svg)

## 🏆 專案願景

本專案為 2025 客家黑客松參賽作品，致力於打造一個創新的客家語數位學習生態系統。透過結合先進的語音合成技術、機器翻譯、自動化工作流程，以及互動式學習設計，我們希望讓客家語的學習變得更加生動有趣、更貼近現代人的學習習慣。

## 📖 專案特色

### 🌟 創新亮點

1. **三大學習模式整合**
   - 📚 **基礎學習模式**：透過單字卡、測驗和即時翻譯建立扎實基礎
   - 📰 **實境學習模式**：每日新聞客語播報，結合時事與語言學習
   - 🎯 **客製化學習模式**：AI 輔助生成個人化學習內容與練習題

2. **智能語音技術**
   - 支援客家語文字轉語音（TTS）
   - 智能語音緩存系統，提升播放效率
   - 並行處理架構，支援大量語音生成

3. **全方位學習體驗**
   - 視覺化學習進度追蹤
   - 互動式練習與即時回饋
   - 支援 Markdown 格式的豐富內容呈現

## 🏗 系統架構

```
2025_hakka_hackathon/
├── backend/                 # FastAPI 後端服務
│   ├── main.py             # 主要 API 服務
│   ├── hakka_trans_module.py    # 客家語翻譯模組
│   ├── hakka_tts_module.py     # 客家語TTS模組
│   ├── course_generator.py     # 課程內容生成器
│   └── output/             # 音頻輸出目錄
├── frontend/               # Vue.js 前端應用
│   ├── src/
│   │   ├── components/     # Vue 組件
│   │   ├── pages/         # 頁面組件
│   │   └── utils/         # 工具函數
│   └── public/            # 靜態資源
├── n8n-workflows/         # n8n 工作流配置
├── docker-compose.yml     # Docker 編排配置

```

## 🛠 技術棧

### 後端技術
- **FastAPI** (0.104.1) - 現代化的 Python Web 框架
- **uvicorn** - ASGI 伺服器
- **gTTS** - Google Text-to-Speech
- **BeautifulSoup4** - 網頁解析
- **pydub** - 音頻處理
- **requests** - HTTP 請求處理

### 前端技術
- **Vue.js 3** - 漸進式 JavaScript 框架
- **Vue Router 4** - 路由管理
- **Vite** - 前端建構工具
- **Axios** - HTTP 客戶端
- **marked** - Markdown 解析器

### 基礎設施
- **n8n** - 工作流自動化平台
- **Docker & Docker Compose** - 容器化部署

## 🚀 快速開始

### 環境需求
- Docker & Docker Compose
- Node.js 18+ (開發環境)
- Python 3.8+ (開發環境)

### 1. 克隆專案
```bash
git clone https://github.com/your-username/2025_hakka_hackathon.git
cd 2025_hakka_hackathon
```

### 2. 環境配置
創建 `.env` 文件並配置必要的環境變數：
```bash
cp .env.example .env
# 編輯 .env 文件，填入必要的配置
```

必要的環境變數：
```env
HAKKA_TRANS_URL_BASE=https://your-translation-service.com
HAKKA_TRANS_URL_TRANS=https://your-translation-service.com/translate
HAKKA_TRANS_USERNAME=your_username
HAKKA_TRANS_PASSWORD=your_password
```

### 3. 使用 Docker 部署（推薦）
```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看服務日誌
docker-compose logs -f
```

### 4. 手動部署（開發環境）

#### 後端服務
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端服務
```bash
cd frontend
npm install
npm run dev
```

## 🌐 服務端點

### 前端應用
- **主應用**: http://localhost:5173
- **學習課程**: http://localhost:5173/course/1

### 後端 API
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/
- **新聞 API**: http://localhost:8000/api/news
- **翻譯 API**: http://localhost:8000/api/translate
- **語音合成 API**: http://localhost:8000/api/tts

### 自動化工作流
- **n8n 界面**: http://localhost:5678

## 🎓 核心功能詳解

### 📚 課程 1：基礎客語學習與翻譯
提供三種學習工具的整合體驗：

#### 單字卡功能
- 50+ 常用客語詞彙與句子
- 支援客語語音播放
- 視覺化進度追蹤

#### 測驗系統
- 隨機題目生成
- 即時答案檢查
- 分數統計系統

#### 即時翻譯
- 中文轉客語翻譯
- 翻譯歷史記錄
- 一鍵語音播放

### 📰 課程 2：每日精選新聞
- **自動新聞抓取**：從 ETtoday 等新聞來源自動獲取最新新聞
- **客語語音轉換**：將新聞內容轉換為客語語音播報
- **字幕同步顯示**：提供同步字幕，幫助學習者理解內容
- **智能分段處理**：自動識別中英文混合內容並分別處理

### 🎯 課程 3：自由訂定學習內容
- **主題自訂**：根據興趣選擇學習主題
- **難度調整**：初級、中級、高級三種難度選擇
- **AI 生成內容**：透過 n8n 工作流程自動生成學習材料
- **練習題生成**：根據內容自動生成相關測驗題目
- **Markdown 支援**：支援豐富的文本格式呈現

## 📝 API 文檔

### 翻譯 API

#### POST `/api/translate`
翻譯中文文本為客語
```json
{
  "text": "你好",
  "index": "default"
}
```

#### POST `/api/translate/course`
課程專用翻譯 API（支援 Markdown 格式）
```json
{
  "text": "要翻譯的內容",
  "index": 1
}
```

### 語音合成 API

#### POST `/api/tts`
生成客語語音
```json
{
  "text": "恱仔細",
  "voice_type": "hakka"
}
```

### 新聞 API

#### GET `/api/news`
獲取隨機新聞內容

#### GET `/api/audio`
生成新聞客語語音播報

### 課程生成 API

#### POST `/api/generate_course`
生成客製化課程內容
```json
{
  "topic": "客家文化",
  "difficulty": "beginner",
  "includeQuiz": true
}
```

### 模組架構

- **hakka_trans_module.py**: 客語翻譯模組，支援 Markdown 格式保留
- **hakka_tts_module.py**: 客語 TTS 模組，處理語音合成
- **course_generator.py**: 課程生成器，與 n8n 工作流程整合

### 環境變數說明

| 變數名稱 | 說明 | 必要 |
|---------|------|------|
| HAKKA_TRANS_URL_BASE | 翻譯服務基礎 URL | ✓ |
| HAKKA_TRANS_USERNAME | 翻譯服務帳號 | ✓ |
| HAKKA_TRANS_PASSWORD | 翻譯服務密碼 | ✓ |
| HAKKA_TTS_URL_BASE | TTS 服務基礎 URL | ✓ |
| HAKKA_TTS_USERNAME | TTS 服務帳號 | ✓ |
| HAKKA_TTS_PASSWORD | TTS 服務密碼 | ✓ |
| COURSE_WEBHOOK_URL | 課程生成 Webhook | ✗ |
| WEBHOOK_TIMEOUT | Webhook 逾時設定 | ✗ |


## 📦 部署

### 生產環境部署
```bash
# 創建生產環境配置
cp docker-compose.yml docker-compose.prod.yml

# 修改生產環境配置
# - 更改資料庫密碼
# - 設置 SSL 證書
# - 配置域名

# 部署到生產環境
docker-compose -f docker-compose.prod.yml up -d
```




<div align="center">
  <b>🌿 為客家語傳承盡一份心力 🌿</b>
  <br>
  <i>本專案為 2025 客家黑客松參賽作品</i>
</div>
