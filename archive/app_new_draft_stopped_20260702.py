# ⚠️ 歸檔草稿，非目前部署版本 ⚠️
# 這是 2026/7/2 晚間開發到一半就中斷的舊版草稿，功能比 app.py 少（例如沒有
# 「自動帶入本月最新一筆紀錄」功能），且自那之後未再更新。
# Streamlit Cloud 目前實際部署、執行中的是專案根目錄的 app.py，
# 之後若要修改稽核表功能，請改 app.py，不要改這支檔案。

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets 設定
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
SPREADSHEET_NAME = "hand-hygiene-new"

# 初始化 Google Sheets 連接
@st.cache_resource
def init_google_sheets():
    """初始化 Google Sheets 連接"""
    try:
        credentials_dict = dict(st.secrets["gcp_service_account"])
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=SCOPES
        )
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open(SPREADSHEET_NAME)
        return spreadsheet
    except Exception as e:
        st.error(f"無法連接到 Google Sheets: {str(e)}")
        return None

def check_login():
    """檢查使用者登入狀態"""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if st.session_state.user_email is None:
        st.title("🔐 手部衛生稽核系統 - 登入")
        st.markdown("### 請使用 Gmail 帳號登入")
        
        email = st.text_input("Gmail 帳號", placeholder="example@gmail.com")
        
        if st.button("登入", type="primary"):
            if email and "@" in email:
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("請輸入有效的 Email 地址")
        return False
    return True

def save_to_google_sheets(record):
    """將記錄保存到 Google Sheets"""
    try:
        spreadsheet = init_google_sheets()
        if spreadsheet is None:
            return False
        
        try:
            worksheet = spreadsheet.worksheet("稽核數據")
        except:
            worksheet = spreadsheet.add_worksheet(title="稽核數據", rows=1000, cols=20)
            headers = list(record.keys())
            worksheet.append_row(headers)
        
        values = list(record.values())
        worksheet.append_row(values)
        return True
    except Exception as e:
        st.error(f"保存失敗: {str(e)}")
        return False


def parse_month_number(month_text):
    month_text = str(month_text).strip()
    digits = "".join(ch for ch in month_text if ch.isdigit())
    if not digits:
        return None
    try:
        month_num = int(digits)
    except ValueError:
        return None
    return month_num if 1 <= month_num <= 12 else None


@st.cache_data(show_spinner=False)
def load_history_records(user_email, target_year, target_month, cache_buster=0):
    """載入指定登入者的歷史紀錄；5日前保留當月與前月。"""
    try:
        spreadsheet = init_google_sheets()
        if spreadsheet is None:
            return []
        # 判斷是否在當月且在 5 日以前，若是則允許顯示前一個月
        from datetime import timezone, timedelta
        taiwan_now = datetime.now(timezone(timedelta(hours=8)))
        is_current_target_month = taiwan_now.year == target_year and taiwan_now.month == target_month
        is_before_cutoff = is_current_target_month and taiwan_now.day <= 5

        allowed_periods = {(target_year, target_month)}
        if is_before_cutoff:
            if target_month == 1:
                allowed_periods.add((target_year - 1, 12))
            else:
                allowed_periods.add((target_year, target_month - 1))

        normalized_email = str(user_email).strip().lower()
        matched_records = []

        # 優先嘗試直接讀取目標工作表，減少 API 呼叫及延遲
        target_sheet_names = [
            f"{target_year}年{target_month}月",
            f"{target_year}年{target_month}",
            f"{target_month}月",
        ]

        worksheets_to_scan = []
        for name in target_sheet_names:
            try:
                ws = spreadsheet.worksheet(name)
                worksheets_to_scan = [ws]
                break
            except Exception:
                continue

        # 若找不到指定工作表，再退回掃描所有工作表（成本較高）
        if not worksheets_to_scan:
            try:
                worksheets_to_scan = spreadsheet.worksheets()
            except Exception:
                return []

        import time
        for worksheet in worksheets_to_scan:
            # 增加簡單重試機制，處理暫時性的 API 錯誤
            records = None
            for attempt in range(3):
                try:
                    records = worksheet.get_all_records()
                    break
                except Exception:
                    time.sleep(0.5 * (attempt + 1))
                    records = None
            if records is None:
                continue

            for record in records:
                record_email = str(record.get("登入者Email", "")).strip().lower()
                if record_email and record_email != normalized_email:
                    continue

                date_text = str(record.get("稽核日期", ""))
                time_text = str(record.get("稽核時間", "00:00:00"))

                try:
                    record_datetime = datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M:%S")
                except Exception:
                    continue

                if (record_datetime.year, record_datetime.month) not in allowed_periods:
                    continue

                month_value = str(record.get("稽核列計月份", record.get("稽核月份", ""))).strip()
                normalized_record = dict(record)
                normalized_record["稽核列計月份"] = month_value or f"{record_datetime.month}月"
                matched_records.append(normalized_record)

        def sort_key(record):
            date_text = str(record.get("稽核日期", ""))
            time_text = str(record.get("稽核時間", "00:00:00"))
            try:
                return datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M:%S")
            except Exception:
                return datetime.min

        return sorted(matched_records, key=sort_key, reverse=True)
    except Exception as e:
        st.warning(f"載入歷史紀錄失敗: {str(e)}")
        return []

# 設置頁面
st.set_page_config(
    page_title="手部衛生稽核系統",
    page_icon="🧼",
    layout="centered"
)

# 檢查登入
if not check_login():
    st.stop()

# 初始化 session state
if 'audit_month' not in st.session_state:
    st.session_state.audit_month = None
if 'auditor' not in st.session_state:
    st.session_state.auditor = None
if 'department' not in st.session_state:
    st.session_state.department = None
if 'staff_category' not in st.session_state:
    st.session_state.staff_category = None
if 'basic_info_completed' not in st.session_state:
    st.session_state.basic_info_completed = False
if 'current_observations' not in st.session_state:
    st.session_state.current_observations = []
if 'history_cache_version' not in st.session_state:
    st.session_state.history_cache_version = 0

# 標題
col_title, col_user = st.columns([3, 1])
with col_title:
    st.title("🧼 手部衛生稽核表")
with col_user:
    st.caption(f"👤 {st.session_state.user_email}")
    if st.button("登出", key="logout"):
        st.session_state.user_email = None
        st.rerun()

st.markdown("---")

current_date = datetime.now(timezone(timedelta(hours=8)))
history_records = load_history_records(
    st.session_state.user_email,
    current_date.year,
    current_date.month,
    st.session_state.history_cache_version,
)

if history_records:
    st.subheader("📊 稽核歷史紀錄")
    history_display_columns = [
        "稽核列計月份",
        "稽核日期",
        "稽核時間",
        "稽核人員",
        "稽核單位",
        "受稽核人員類別",
        "手部衛生時機",
        "執行方式",
        "正確性",
        "不正確原因",
        "備註",
    ]
    history_df = pd.DataFrame(history_records)
    display_columns = [column for column in history_display_columns if column in history_df.columns]
    if display_columns:
        st.dataframe(history_df[display_columns], use_container_width=True, hide_index=True)
    else:
        st.dataframe(history_df, use_container_width=True, hide_index=True)

# 步驟1: 填寫基本資料
if not st.session_state.basic_info_completed:
    st.header("📋 步驟1: 填寫基本資料")
    
    col1, col2 = st.columns(2)
    
    with col1:
        audit_month = st.selectbox(
            "📅 稽核列計月份",
            ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
            key="audit_month_select"
        )
        
        auditor = st.text_input(
            "👨‍⚕️ 稽核人員姓名",
            value="",
            placeholder="請輸入姓名",
            key="auditor_input"
        )
    
    with col2:
        department = st.selectbox(
            "🏥 隸屬稽核單位/病房",
            ["ER", "HDR", "OPD", "ICU", "RCW", "7W", "8W", "9W", "11W", 
             "內科", "外科", "精神科", "復健科", "松1.2", "松3", "松5.6", 
             "康", "日照", "其他(請註明)"],
            key="department_select"
        )
        
        if department == "其他(請註明)":
            department = st.text_input("請註明單位", key="department_other")
        
        staff_category = st.selectbox(
            "👥 受稽核人員類別",
            ["護理師", "照服員", "傳送/班長", "病房服務員", "內科醫師", "外科醫師",
             "內科專師", "外科專師", "職能治療", "物理治療", "營養師", "呼吸治療師",
             "門診助理員", "語言治療師", "社工師", "醫檢師", "放射師", "精神科醫師",
             "精神科專師", "精神科職能治療", "心理師", "其他(請註明)"],
            key="staff_category_select"
        )
        
        if staff_category == "其他(請註明)":
            staff_category = st.text_input("請註明人員類別", key="staff_category_other")
    
    st.markdown("---")
    
    if st.button("✅ 確認基本資料，開始稽核", type="primary", use_container_width=True):
        if auditor and department and staff_category:
            st.session_state.audit_month = audit_month
            st.session_state.auditor = auditor
            st.session_state.department = department
            st.session_state.staff_category = staff_category
            st.session_state.basic_info_completed = True
            st.rerun()
        else:
            st.error("請填寫所有必填欄位！")

else:
    # 步驟2: 進行手部衛生觀察
    st.header("🔍 步驟2: 手部衛生行為觀察")
    
    # 顯示當前稽核資訊
    st.info(f"""
    **當前稽核資訊**  
    📅 稽核月份: {st.session_state.audit_month}  
    👨‍⚕️ 稽核人員: {st.session_state.auditor}  
    🏥 稽核單位: {st.session_state.department}  
    👥 受稽核人員: {st.session_state.staff_category}
    """)
    
    st.markdown("---")
    
    # 1. 選擇觀察時機
    st.subheader("1️⃣ 選擇手部衛生時機")
    hand_hygiene_moment = st.radio(
        "請點選觀察時機",
        [
            "時機1: 接觸病人前",
            "時機2: 執行清潔/無菌操作技術前",
            "時機3: 暴露病人體液風險後",
            "時機4: 接觸病人後",
            "時機5: 接觸病人周遭環境後"
        ],
        key="hand_hygiene_moment"
    )
    
    st.markdown("---")
    
    # 2. 選擇手部衛生執行方式
    st.subheader("2️⃣ 手部衛生執行方式")
    hygiene_method = st.radio(
        "請選擇執行方式（三選一）",
        ["乾洗手（酒精性乾洗手液）", "濕洗手（肥皂和水）", "沒有洗手"],
        key="hygiene_method"
    )
    
    # 3. 如果有洗手，評估正確性
    technique_correct = None
    incorrect_reason = None
    
    if hygiene_method != "沒有洗手":
        st.markdown("---")
        st.subheader("3️⃣ 執行正確性評估")
        
        technique_correct = st.radio(
            "請評估正確性",
            ["正確(七步驟完全正確)", "不正確"],
            key="technique_correct"
        )
        
        if technique_correct == "不正確":
            st.write("**請選擇不正確原因：**")
            incorrect_reason = st.radio(
                "不正確原因",
                ["步驟不完整", "戴手套洗手", "濕洗手後未擦乾", "其他(請註明)"],
                key="incorrect_reason"
            )
            
            if incorrect_reason == "其他(請註明)":
                incorrect_reason = st.text_input("請註明原因", key="incorrect_reason_other")
    
    # 備註
    st.markdown("---")
    notes = st.text_area("備註（選填）", placeholder="請填寫其他觀察事項", height=80, key="notes")
    
    # 提交當前觀察
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ 提交此次觀察", type="primary", use_container_width=True):
            # 驗證必填欄位
            if hygiene_method != "沒有洗手" and technique_correct is None:
                st.error("請評估執行正確性！")
            elif technique_correct == "不正確" and not incorrect_reason:
                st.error("請選擇不正確原因！")
            else:
                # 創建觀察記錄
                observation = {
                    "稽核月份": st.session_state.audit_month,
                    "稽核日期": datetime.now().strftime("%Y-%m-%d"),
                    "稽核時間": datetime.now().strftime("%H:%M:%S"),
                    "稽核人員": st.session_state.auditor,
                    "稽核單位": st.session_state.department,
                    "受稽核人員類別": st.session_state.staff_category,
                    "手部衛生時機": hand_hygiene_moment,
                    "執行方式": hygiene_method,
                    "正確性": technique_correct if technique_correct else "未評估(沒有洗手)",
                    "不正確原因": incorrect_reason if incorrect_reason else "無",
                    "備註": notes if notes else "無",
                    "遵從率": "是" if hygiene_method != "沒有洗手" else "否"
                }
                
                # 保存到 Google Sheets
                with st.spinner("正在保存到雲端..."):
                    if save_to_google_sheets(observation):
                        st.session_state.history_cache_version += 1
                        st.session_state.current_observations.append(observation)
                        st.success("✅ 觀察記錄已成功保存！")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("⚠️ 保存失敗，請檢查網路連接")
    
    with col2:
        if st.button("🔄 繼續觀察", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("👤 更換受稽人員", use_container_width=True):
            st.session_state.staff_category = None
            st.session_state.basic_info_completed = False
            st.rerun()
    
    st.markdown("---")
    
    if st.button("🏁 結束觀察", type="secondary", use_container_width=True):
        # 重置所有狀態
        st.session_state.audit_month = None
        st.session_state.auditor = None
        st.session_state.department = None
        st.session_state.staff_category = None
        st.session_state.basic_info_completed = False
        st.session_state.current_observations = []
        st.success("稽核已結束，可以開始新的稽核。")
        st.rerun()
    
    # 顯示當前會話的觀察記錄
    if st.session_state.current_observations:
        st.markdown("---")
        st.subheader("📝 本次稽核的觀察記錄")
        df_current = pd.DataFrame(st.session_state.current_observations)
        st.dataframe(df_current, use_container_width=True)

# 頁尾
st.markdown("---")
st.caption("手部衛生稽核系統 v3.0 | 數據同步至 Google 雲端")
