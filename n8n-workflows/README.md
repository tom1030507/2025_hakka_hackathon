# n8n Workflows 目錄

這個目錄包含自定義的 n8n workflow 和相關設定。

## 目錄結構

```
n8n-workflows/
├── import/                     # 要匯入的 workflow 檔案
│   └── hakka-news-automation.json # 客家新聞自動化範例
├── backup/                     # workflow 備份檔案
└── credentials/                # 認證設定檔案
    └── sample-auth.json       # 範例認證設定
```

## 使用方式

### 1. 啟動 n8n
```bash
docker-compose up -d
```

### 2. 訪問 n8n 介面
http://localhost:5678
- 用戶名: admin
- 密碼: password

### 3. 匯入 workflow
1. 在 n8n 介面點擊「Import from file」
2. 選擇 `import/` 目錄中的 JSON 檔案
3. 確認匯入設定

### 4. 設定認證
如果 workflow 需要 API 認證：
1. 進入 Settings > Credentials
2. 參考 `credentials/` 目錄中的範例設定

## 範例 Workflow 說明

### hakka-news-automation.json
- **功能**: 自動獲取客家新聞並處理
- **觸發**: 每小時執行一次
- **流程**: 
  1. 呼叫後端 API 獲取新聞
  2. 檢查新聞內容是否存在
  3. 處理新聞資料
  4. 發送通知

## 注意事項

- workflow 檔案必須是有效的 JSON 格式
- 認證資料請勿包含敏感資訊
- 備份目錄會自動儲存 n8n 的備份檔案