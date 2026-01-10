# Google Sheets 連接設定指南

## 📋 前置準備檢查清單

✅ Google Cloud 專案已建立: **Hand Hygiene New**  
✅ Google Drive API 已啟用  
✅ Google Sheets API 已啟用  
✅ 服務帳號已建立: **audit-bot@hand-hygiene-new.iam.gserviceaccount.com**  
✅ Google 試算表已建立: **hand-hygiene-new**  
✅ 試算表已共用給服務帳號（編輯權限）

---

## 🔧 設定步驟

### 步驟 1：下載服務帳號金鑰

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 選擇專案：**Hand Hygiene New**
3. 前往「IAM 與管理」→「服務帳號」
4. 找到 `audit-bot@hand-hygiene-new.iam.gserviceaccount.com`
5. 點擊「金鑰」→「新增金鑰」→「建立新金鑰」
6. 選擇 **JSON** 格式
7. 下載 JSON 檔案（例如：`hand-hygiene-new-xxxxx.json`）

### 步驟 2：設定 secrets.toml

1. 開啟下載的 JSON 檔案
2. 將內容複製到 `.streamlit/secrets.toml`

#### 方法 A：自動轉換（推薦）

將整個 JSON 內容貼入以下格式：

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
your-private-key-content-here
-----END PRIVATE KEY-----"""
client_email = "audit-bot@hand-hygiene-new.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
universe_domain = "googleapis.com"
```

#### 方法 B：逐項複製

從 JSON 檔案中複製對應的值到 `secrets.toml`：

- `project_id` → 專案 ID
- `private_key_id` → 私鑰 ID
- `private_key` → 私鑰（注意：使用三引號 `"""` 包住整個私鑰）
- `client_email` → 服務帳號電子郵件
- `client_id` → 客戶端 ID
- `client_x509_cert_url` → 憑證 URL

⚠️ **重要注意事項：**
- `private_key` 必須使用三引號 `"""` 包住
- 保持私鑰的完整格式，包含換行符號
- 不要刪除 `-----BEGIN PRIVATE KEY-----` 和 `-----END PRIVATE KEY-----`

### 步驟 3：安裝套件

在專案目錄下執行：

```bash
pip install -r requirements.txt
```

### 步驟 4：確認 Google 試算表權限

1. 開啟試算表：[https://docs.google.com/spreadsheets/](https://docs.google.com/spreadsheets/)
2. 找到 **hand-hygiene-new**
3. 點擊「共用」
4. 確認 `audit-bot@hand-hygiene-new.iam.gserviceaccount.com` 擁有**編輯者**權限

### 步驟 5：執行應用程式

```bash
streamlit run app.py
```

---

## 🌐 部署到網路（讓其他人填寫）

### 選項 A：Streamlit Community Cloud（免費，推薦）

1. 前往 [share.streamlit.io](https://share.streamlit.io/)
2. 使用 GitHub 帳號登入
3. 將專案上傳到 GitHub（注意：**不要**上傳 `secrets.toml`）
4. 在 Streamlit Cloud 新增應用程式
5. 在部署設定中，點擊「Advanced settings」→「Secrets」
6. 將 `secrets.toml` 的內容貼上
7. 點擊「Deploy」

部署後，你會獲得一個公開網址，例如：
`https://your-app-name.streamlit.app`

### 選項 B：其他雲端平台

- **Heroku**: [部署指南](https://docs.streamlit.io/deploy/tutorials/heroku)
- **Google Cloud Run**: [部署指南](https://docs.streamlit.io/deploy/tutorials/gcp)
- **AWS**: [部署指南](https://docs.streamlit.io/deploy/tutorials/aws)

---

## ✅ 測試連接

執行應用程式後，檢查：

1. 側邊欄應顯示「✅ 已連接到雲端」
2. 填寫並提交一筆測試數據
3. 開啟 Google 試算表確認數據已寫入

---

## 🔒 安全提醒

⚠️ **絕對不要**將以下檔案上傳到 GitHub 或公開分享：
- `.streamlit/secrets.toml`
- 服務帳號 JSON 金鑰檔案

建議在 `.gitignore` 中加入：
```
.streamlit/secrets.toml
*.json
__pycache__/
*.pyc
```

---

## 🐛 常見問題排解

### 錯誤：無法連接到 Google Sheets

**可能原因：**
1. `secrets.toml` 設定錯誤
   - 解決方法：檢查所有欄位是否正確複製
   
2. 試算表沒有共用給服務帳號
   - 解決方法：在 Google 試算表中新增 `audit-bot@hand-hygiene-new.iam.gserviceaccount.com` 為編輯者

3. API 未啟用
   - 解決方法：在 Google Cloud Console 確認已啟用 Google Sheets API 和 Google Drive API

### 錯誤：Private key 格式錯誤

**解決方法：**
確保 `private_key` 使用三引號包住：
```toml
private_key = """-----BEGIN PRIVATE KEY-----
完整的私鑰內容
-----END PRIVATE KEY-----"""
```

### 錯誤：權限不足

**解決方法：**
確保服務帳號具有以下權限：
- Google Sheets API（已啟用）
- Google Drive API（已啟用）
- 試算表共用權限為「編輯者」

---

## 📞 需要協助？

如有任何問題，請檢查：
1. [Streamlit 文檔](https://docs.streamlit.io/)
2. [gspread 文檔](https://docs.gspread.org/)
3. [Google Cloud 文檔](https://cloud.google.com/docs)

---

**設定完成後，您的應用程式就可以多人同時在不同網路下使用，所有數據都會即時同步到 Google 雲端！** 🎉
