# 手部衛生稽核系統

這是一個基於 Streamlit 的手部衛生遵從率與行為稽核數據收集系統，支援多人協作並即時同步到 Google 雲端試算表。

## ✨ 功能特色

- ✅ 完整的手部衛生稽核表單
- ✅ WHO五大手部衛生時機選項
- ✅ **即時雲端數據同步（Google Sheets）**
- ✅ **多人同時填寫，不同網路下皆可使用**
- ✅ 遵從率自動計算
- ✅ CSV 檔案匯出功能
- ✅ 友善的使用者介面
- ✅ 數據永久保存在雲端

## 🔧 雲端設定資訊

- **Google Cloud 專案**: Hand Hygiene New
- **試算表名稱**: hand-hygiene-new
- **服務帳號**: audit-bot@hand-hygiene-new.iam.gserviceaccount.com

## 📦 安裝步驟

### 1. 安裝所需套件

```bash
pip install -r requirements.txt
```

### 2. 設定 Google Cloud 憑證

請參考 [SETUP_GUIDE.md](SETUP_GUIDE.md) 的詳細說明。

**快速步驟：**
1. 從 Google Cloud Console 下載服務帳號 JSON 金鑰
2. 將金鑰內容填入 `.streamlit/secrets.toml`
3. 確認試算表已共用給服務帳號

## 🚀 執行方式

在專案目錄下執行：
```bash
streamlit run app.py
```

系統會自動在瀏覽器開啟 Web 應用程式（預設：http://localhost:8501）

## 🌐 部署到網路（推薦）

### Streamlit Community Cloud（免費）

1. 將專案上傳到 GitHub（不要上傳 `secrets.toml`）
2. 前往 [share.streamlit.io](https://share.streamlit.io/)
3. 連接 GitHub 倉庫並部署
4. 在部署設定中貼上 secrets 內容
5. 獲得公開網址，分享給所有填寫者

詳細步驟請參考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📝 使用說明

### 1. 填寫基本資訊
- 在側邊欄填寫稽核日期、時間、稽核人員和單位

### 2. 記錄稽核內容
- 選擇受稽核人員類別
- 選擇手部衛生時機
- 記錄是否執行手部衛生
- 記錄衛生方式和技術正確性
- 記錄其他觀察事項

### 3. 提交與管理
- 點擊「提交稽核紀錄」自動保存到雲端
- 查看統計摘要和遵從率
- 可隨時重新載入最新雲端數據
- 可下載 CSV 檔案進行進一步分析

## 📊 數據欄位說明

- **稽核日期/時間**：稽核執行的日期和時間
- **稽核人員**：執行稽核的人員姓名
- **稽核單位**：被稽核的單位或病房
- **人員類別**：被稽核人員的職類
- **手部衛生時機**：WHO五大時機
- **是否執行**：是否執行手部衛生
- **衛生方式**：乾洗手或濕洗手
- **技術正確**：技術執行是否正確
- **遵從率**：自動計算的遵從情況

## 🔒 數據安全

- ✅ 數據加密傳輸
- ✅ Google Cloud 企業級安全保護
- ✅ 服務帳號權限隔離
- ✅ 僅授權人員可存取試算表

## ⚠️ 注意事項

- 📌 首次使用前必須完成 Google Cloud 設定
- 📌 需要網路連接才能同步數據
- 📌 定期備份 Google 試算表數據
- 📌 不要公開分享 `secrets.toml` 或服務帳號金鑰

## 🆘 故障排除

如果遇到連接問題：

1. 檢查側邊欄的連接狀態指示
2. 確認 `secrets.toml` 設定正確
3. 確認試算表共用給服務帳號
4. 確認 Google Sheets API 已啟用
5. 點擊「重新載入雲端數據」按鈕

詳細排障步驟請參考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📞 技術支援

如有任何問題或建議，請查看：
- [完整設定指南](SETUP_GUIDE.md)
- [Streamlit 官方文檔](https://docs.streamlit.io/)
- [Google Cloud 文檔](https://cloud.google.com/docs)

---

**版本**: v2.0  
**最後更新**: 2026-01-10
