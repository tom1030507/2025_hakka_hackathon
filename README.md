# 2025 客家黑客松專案 - 客家語學習平台

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-red.svg)

## 📖 專案簡介

這是一個為 2025 客家黑客松開發的智能客家語學習平台，整合了語音合成、翻譯服務、新聞播報和互動學習功能。平台提供沉浸式的客家語學習體驗，幫助使用者更有效地學習和保存客家文化。

## ✨ 主要功能

### 🎯 核心功能
- **智能翻譯服務**: 中文與客家語之間的雙向翻譯
- **客家語音合成**: 高品質的客家語 TTS（文字轉語音）技術
- **新聞播報系統**: 自動抓取新聞並轉換為客家語音播報
- **互動學習課程**: 多元化的客家語學習教材
- **進度追蹤**: 個人化學習進度管理系統

### 🛠 技術功能
- **自動化工作流**: 使用 n8n 進行新聞處理自動化
- **音頻緩存機制**: 智能音頻文件管理和緩存
- **批量翻譯處理**: 支援大量文本的批次翻譯
- **RESTful API**: 完整的後端 API 服務

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
└── init-db.sql           # 資料庫初始化腳本
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
- **PostgreSQL 15** - 關聯式資料庫
- **n8n** - 工作流自動化平台
- **Docker & Docker Compose** - 容器化部署
- **Nginx** - 反向代理（可選）

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

#### 資料庫
```bash
# 啟動 PostgreSQL
docker run -d \
  --name hakka-postgres \
  -e POSTGRES_DB=hakka_hackathon \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine
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
  - 用戶名: `admin`
  - 密碼: `password`

### 資料庫
- **PostgreSQL**: localhost:5432
  - 資料庫: `hakka_hackathon`
  - 用戶名: `postgres`
  - 密碼: `password`

## 📝 API 使用說明

### 翻譯服務
```bash
# 單個文本翻譯
curl -X POST "http://localhost:8000/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好", "index": "test"}'

# 批量翻譯
curl -X POST "http://localhost:8000/api/translate/batch" \
  -H "Content-Type: application/json" \
  -d '["你好", "謝謝", "再見"]'
```

### 語音合成
```bash
curl -X POST "http://localhost:8000/api/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好", "voice_type": "hakka"}'
```

### 新聞播報
```bash
# 獲取新聞內容
curl "http://localhost:8000/api/news"

# 生成語音播報
curl "http://localhost:8000/api/audio"
```

## 🎓 學習功能

### 課程結構
- **課程 1**: 基礎發音和問候語
- **課程 2**: 日常對話和常用詞彙
- **課程 3**: 進階語法和文化內容

### 學習工具
- **互動式練習**: 聽力、口說、閱讀綜合練習
- **進度追蹤**: 個人化學習歷程記錄
- **語音評估**: 發音準確度評估
- **新聞播報**: 實時新聞客家語播報

## 🔧 開發指南

### 添加新的翻譯功能
1. 修改 `backend/hakka_trans_module.py`
2. 更新 API 端點在 `backend/main.py`
3. 測試翻譯功能

### 添加新的課程內容
1. 在 `frontend/src/components/pages/Courses/` 創建新的 Vue 組件
2. 更新路由配置在 `frontend/src/router.js`
3. 添加課程資源到 `frontend/public/`

### 自定義 n8n 工作流
1. 在 n8n 界面創建新的工作流
2. 導出工作流 JSON 文件
3. 將文件保存到 `n8n-workflows/import/`

## 🧪 測試

### 後端測試
```bash
cd backend
pytest tests/
```

### 前端測試
```bash
cd frontend
npm run test
```

### API 測試
使用提供的 Postman 集合或直接訪問 http://localhost:8000/docs 進行交互式測試。

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

### 備份和還原
```bash
# 備份資料庫
docker-compose exec db pg_dump -U postgres hakka_hackathon > backup.sql

# 還原資料庫
docker-compose exec -T db psql -U postgres hakka_hackathon < backup.sql
```

## 🤝 貢獻指南

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案使用 MIT 授權。詳見 [LICENSE](LICENSE) 文件。

## 🙋‍♂️ 支援

如有問題或建議，請：
- 提交 [Issue](https://github.com/your-username/2025_hakka_hackathon/issues)
- 發送郵件至 your-email@example.com
- 參與 [Discussions](https://github.com/your-username/2025_hakka_hackathon/discussions)

## 🎯 未來規劃

- [ ] 支援更多客家語方言
- [ ] 添加語音識別功能
- [ ] 開發行動應用程式
- [ ] 整合 AI 聊天機器人
- [ ] 建立學習社群功能
- [ ] 添加遊戲化學習元素

## 🏆 致謝

感謝所有為客家語保存和推廣貢獻力量的開發者和語言學家。

---

*本專案為 2025 客家黑客松參賽作品，致力於客家文化的數位保存與傳承。*