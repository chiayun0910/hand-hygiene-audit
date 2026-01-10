# 部署指南

## 步驟1：上傳到 GitHub

在 VS Code 終端機依序執行以下指令：

```powershell
cd "d:\作業\手部衛生稽核2"
git init
git add app.py requirements.txt README.md
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/chiayun0910/hand-hygiene-audit.git
git push -u origin main
```

## 步驟2：在 GitHub 創建 Repository

1. 前往 https://github.com/new
2. Repository name: `hand-hygiene-audit`
3. 設為 **Private**
4. 不要勾選任何選項
5. 點擊 **Create repository**

## 步驟3：部署到 Streamlit Cloud

1. 前往 https://share.streamlit.io/
2. 用 GitHub 登入
3. 點擊 **New app**
4. 選擇：
   - Repository: `chiayun0910/hand-hygiene-audit`
   - Branch: `main`
   - Main file: `app.py`
5. 點擊 **Advanced settings**
6. 在 **Secrets** 貼上 key.json 內容（見下方格式）
7. 點擊 **Deploy!**

## Secrets 格式

打開您的 `key.json` 檔案，按照以下格式轉換：

```toml
[gcp_service_account]
type = "service_account"
project_id = "從 key.json 複製"
private_key_id = "從 key.json 複製"
private_key = "從 key.json 複製（保持原樣包含換行符）"
client_email = "從 key.json 複製"
client_id = "從 key.json 複製"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "從 key.json 複製"
```

完成後您會得到一個網址，例如：`https://hand-hygiene-audit.streamlit.app`
