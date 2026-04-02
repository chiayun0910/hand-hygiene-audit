import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import gspread

# Google Sheets 設定
SPREADSHEET_NAME = "hand-hygiene-new"

# 初始化 Google Sheets 連接
@st.cache_resource
def init_google_sheets():
    """初始化 Google Sheets 連接"""
    try:
        # 嘗試使用本地 key.json（本地開發環境）
        import os
        if os.path.exists('key.json'):
            gc = gspread.service_account(filename='key.json')
        else:
            # 使用 Streamlit secrets（雲端環境）
            gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        
        sh = gc.open(SPREADSHEET_NAME)
        return sh
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

def save_to_google_sheets(record, audit_month):
    """將記錄保存到 Google Sheets"""
    try:
        spreadsheet = init_google_sheets()
        if spreadsheet is None:
            return False
        
        # 根據稽核月份生成工作表名稱，例如：2026年1月
        from datetime import datetime
        current_year = datetime.now().year
        sheet_name = f"{current_year}年{audit_month}"
        
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except:
            # 工作表不存在，創建新的
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            headers = list(record.keys())
            worksheet.append_row(headers)
        
        values = list(record.values())
        worksheet.append_row(values)
        return True
    except Exception as e:
        st.error(f"保存失敗: {str(e)}")
        return False

def load_monthly_records(user_email, target_year, target_month):
    """載入指定實際月份、指定登入者的所有紀錄"""
    try:
        spreadsheet = init_google_sheets()
        if spreadsheet is None:
            return []

        def extract_month_from_sheet_title(sheet_title):
            """從工作表名稱（例：2026年3月、3月、2026/3）解析月份"""
            import re
            title = str(sheet_title).strip()
            
            # 提取所有數字
            digits = re.findall(r'\d+', title)
            
            if not digits:
                return ""
            
            # 方法1：如果有"年"和"月"，提取它們之間的數字
            if "年" in title and "月" in title:
                try:
                    year_idx = title.find("年")
                    month_idx = title.find("月", year_idx)
                    month_str = title[year_idx+1:month_idx].strip()
                    month_digits = ''.join(c for c in month_str if c.isdigit())
                    if month_digits:
                        month_num = int(month_digits)
                        if 1 <= month_num <= 12:
                            return f"{month_num}月"
                except Exception:
                    pass
            
            # 方法2：查找1-12之間的數字，優先選最後出現的
            potential_months = [int(d) for d in digits if int(d) >= 1 and int(d) <= 12]
            if potential_months:
                return f"{potential_months[-1]}月"
            
            return ""

        normalized_email = str(user_email).strip().lower()
        matched_records = []

        for worksheet in spreadsheet.worksheets():
            sheet_month_fallback = extract_month_from_sheet_title(worksheet.title)

            try:
                records = worksheet.get_all_records()
            except Exception:
                continue

            for record in records:
                if str(record.get("登入者Email", "")).strip().lower() != normalized_email:
                    continue

                date_text = str(record.get("稽核日期", ""))
                time_text = str(record.get("稽核時間", "00:00:00"))

                try:
                    record_datetime = datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M:%S")
                except Exception:
                    continue

                if record_datetime.year == target_year and record_datetime.month == target_month:
                    month_value = str(record.get("稽核列計月份", "")).strip()
                    legacy_month_value = str(record.get("稽核月份", "")).strip()
                    resolved_month = month_value or legacy_month_value or sheet_month_fallback

                    normalized_record = dict(record)
                    normalized_record["稽核列計月份"] = resolved_month
                    matched_records.append(normalized_record)

        def sort_key(record):
            date_text = str(record.get("稽核日期", ""))
            time_text = str(record.get("稽核時間", "00:00:00"))
            try:
                return datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M:%S")
            except Exception:
                return datetime.min

        return sorted(matched_records, key=sort_key)
    except Exception as e:
        st.warning(f"載入歷史紀錄失敗: {str(e)}")
        return []

def load_latest_monthly_record(user_email, target_year, target_month):
    """載入指定實際月份、指定登入者的最新一筆紀錄"""
    try:
        matched_records = load_monthly_records(user_email, target_year, target_month)
        if not matched_records:
            return None
        return matched_records[-1]
    except Exception as e:
        st.warning(f"載入歷史紀錄失敗: {str(e)}")
        return None


def apply_record_defaults(record):
    """將歷史紀錄回填到表單預設值"""
    if not record:
        return

    department = record.get("稽核者單位")
    auditor = record.get("稽核人員")
    staff_category = record.get("受稽核人員類別")
    staff_unit = record.get("受稽核者單位")

    departments = ["ER", "HDR", "OPD", "OPD(市區)", "ICU", "RCW", "7W", "8W", "9W", "11W",
                   "內科", "外科", "精神科", "復健科", "放射科", "檢驗科", "感管中心",
                   "松齡1.2區", "松齡3區", "松齡5.6區", "康寧居", "日照", "其他(請註明)"]

    staff_categories = ["護理師", "照服員", "傳送/班長", "病房服務員", "內科醫師", "外科醫師",
                       "內科專師", "外科專師", "職能治療", "物理治療", "營養師", "呼吸治療師",
                       "門診助理員", "語言治療師", "社工師", "醫檢師", "放射師", "精神科醫師",
                       "精神科專師", "精神科職能治療", "心理師", "其他(請註明)"]

    if department:
        if department in departments:
            st.session_state.department = department
        else:
            st.session_state.department = "其他(請註明)"
            st.session_state.department_other = department
    if auditor:
        st.session_state.auditor = auditor
    if staff_category:
        if staff_category in staff_categories:
            st.session_state.staff_category = staff_category
        else:
            st.session_state.staff_category = "其他(請註明)"
            st.session_state.staff_category_other = staff_category

    if staff_unit:
        if department and staff_unit == department:
            st.session_state.staff_unit_type = "同隸屬稽核單位/病房"
        else:
            st.session_state.staff_unit_type = "另選隸屬單位"
            if staff_unit in departments:
                st.session_state.staff_unit = staff_unit
            else:
                st.session_state.staff_unit = "其他(請註明)"
                st.session_state.staff_unit_other = staff_unit

    if record.get("手部衛生時機"):
        st.session_state.hand_hygiene_moment = record["手部衛生時機"]
    if record.get("手部衛生方式"):
        st.session_state.hygiene_method = record["手部衛生方式"]
    if record.get("手部衛生正確性") in ["正確(七步驟完全正確)", "不正確"]:
        st.session_state.technique_correct = record["手部衛生正確性"]
    if record.get("備註"):
        st.session_state.notes = record["備註"]


def format_history_record(record):
    """整理要顯示的歷史紀錄欄位"""
    if not record:
        return None

    audit_month_value = record.get("稽核列計月份", record.get("稽核月份", ""))

    display_keys = [
        "稽核列計月份",
        "稽核日期",
        "稽核時間",
        "稽核者單位",
        "稽核人員",
        "受稽核人員類別",
        "受稽核者單位",
        "手部衛生時機",
        "手部衛生方式",
        "手部衛生正確性",
        "不正確原因",
    ]
    if "備註" in record:
        display_keys.append("備註")

    history_record = {key: record.get(key, "") for key in display_keys}
    history_record["稽核列計月份"] = audit_month_value
    return history_record

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
    st.session_state.audit_month = ""
if 'auditor' not in st.session_state:
    st.session_state.auditor = ""
if 'department' not in st.session_state:
    st.session_state.department = "ER"
if 'staff_category' not in st.session_state:
    st.session_state.staff_category = "護理師"
if 'current_observations' not in st.session_state:
    st.session_state.current_observations = []
if 'latest_monthly_record' not in st.session_state:
    st.session_state.latest_monthly_record = None
if 'latest_monthly_record_key' not in st.session_state:
    st.session_state.latest_monthly_record_key = None
if 'monthly_history_records' not in st.session_state:
    st.session_state.monthly_history_records = []

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

# 基本資料區塊
st.header("📋 稽核基本資料")

# 第一列：稽核月份、稽核單位、稽核人員
col1, col2, col3 = st.columns(3)

with col1:
    # 限制月份選擇：每月5日後只能選擇當月，5日前可選擇當月或前一個月
    current_date = datetime.now()
    current_month = current_date.month
    current_day = current_date.day
    all_months = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    
    # 根據日期決定可選擇的月份
    if current_day <= 5:
        # 5日前（含5日），可選擇當月或前一個月
        if current_month == 1:
            # 1月時，前一個月是去年12月，但只顯示1月
            available_months = [all_months[0]]
        else:
            # 其他月份，可選擇前一個月和當月（前一個月在前）
            available_months = [all_months[current_month - 2], all_months[current_month - 1]]
    else:
        # 5日後，只能選擇當月
        available_months = [all_months[current_month - 1]]
    
    # 預設選擇當月（當月一定在可選範圍內）
    current_month_str = all_months[current_month - 1]
    default_index = available_months.index(current_month_str)
    
    help_text = f"目前是{current_month}月{current_day}日，"
    if current_day <= 5:
        help_text += "可選擇當月或前一個月"
    else:
        help_text += "只能選擇當月"
    
    audit_month = st.selectbox(
        "📅 稽核列計月份",
        available_months,
        index=default_index,
        help=help_text
    )

record_context_key = f"{st.session_state.user_email}|{current_date.strftime('%Y-%m')}"
monthly_records = load_monthly_records(
    st.session_state.user_email,
    current_date.year,
    current_date.month,
)
st.session_state.latest_monthly_record = monthly_records[-1] if monthly_records else None
if st.session_state.latest_monthly_record_key != record_context_key:
    apply_record_defaults(st.session_state.latest_monthly_record)
st.session_state.latest_monthly_record_key = record_context_key
st.session_state.monthly_history_records = monthly_records

with col2:
    departments = ["ER", "HDR", "OPD", "OPD(市區)", "ICU", "RCW", "7W", "8W", "9W", "11W", 
                   "內科", "外科", "精神科", "復健科", "放射科", "檢驗科", "感管中心", 
                   "松齡1.2區", "松齡3區", "松齡5.6區", "康寧居", "日照", "其他(請註明)"]
    
    department = st.selectbox(
        "🏥 隸屬稽核單位/病房",
        departments,
        index=departments.index(st.session_state.department) if st.session_state.department in departments else 0,
        key="department_select"
    )
    
    if department == "其他(請註明)":
        department = st.text_input("請註明單位", key="department_other")
    
    st.session_state.department = department

with col3:
    auditor = st.text_input(
        "👨‍⚕️ 稽核人員姓名",
        value=st.session_state.auditor,
        placeholder="請輸入姓名",
        key="auditor_input"
    )
    st.session_state.auditor = auditor

# 第二列：受稽核人員類別、受稽核人員單位
col1, col2 = st.columns(2)

with col1:
    staff_category = st.selectbox(
        "👥 受稽核人員類別",
        ["護理師", "照服員", "傳送/班長", "病房服務員", "內科醫師", "外科醫師",
         "內科專師", "外科專師", "職能治療", "物理治療", "營養師", "呼吸治療師",
         "門診助理員", "語言治療師", "社工師", "醫檢師", "放射師", "精神科醫師",
         "精神科專師", "精神科職能治療", "心理師", "其他(請註明)"],
        index=["護理師", "照服員", "傳送/班長", "病房服務員", "內科醫師", "外科醫師",
               "內科專師", "外科專師", "職能治療", "物理治療", "營養師", "呼吸治療師",
               "門診助理員", "語言治療師", "社工師", "醫檢師", "放射師", "精神科醫師",
               "精神科專師", "精神科職能治療", "心理師", "其他(請註明)"].index(st.session_state.staff_category) if st.session_state.staff_category in ["護理師", "照服員", "傳送/班長", "病房服務員", "內科醫師", "外科醫師", "內科專師", "外科專師", "職能治療", "物理治療", "營養師", "呼吸治療師", "門診助理員", "語言治療師", "社工師", "醫檢師", "放射師", "精神科醫師", "精神科專師", "精神科職能治療", "心理師", "其他(請註明)"] else 0,
        key="staff_category_select"
    )
    
    if staff_category == "其他(請註明)":
        staff_category = st.text_input("請註明人員類別", key="staff_category_other")
    
    st.session_state.staff_category = staff_category

with col2:
    # 初始化 staff_unit_type
    if 'staff_unit_type' not in st.session_state:
        st.session_state.staff_unit_type = "同隸屬稽核單位/病房"
    
    staff_unit_type = st.radio(
        "🏫 受稽核人員單位",
        ["同隸屬稽核單位/病房", "另選隸屬單位"],
        key="staff_unit_type_select",
        horizontal=True
    )
    st.session_state.staff_unit_type = staff_unit_type
    
    # 如果選擇「另選隸屬單位」，顯示單位選擇
    if staff_unit_type == "另選隸屬單位":
        if 'staff_unit' not in st.session_state:
            st.session_state.staff_unit = "ER"
        
        staff_unit = st.selectbox(
            "選擇單位",
            departments,
            index=departments.index(st.session_state.staff_unit) if st.session_state.staff_unit in departments else 0,
            key="staff_unit_select",
            label_visibility="collapsed"
        )
        
        if staff_unit == "其他(請註明)":
            staff_unit = st.text_input("請註明單位", key="staff_unit_other")
        
        st.session_state.staff_unit = staff_unit
    else:
        st.session_state.staff_unit = st.session_state.department

st.markdown("---")

# 手部衛生觀察區塊
st.header("🔍 手部衛生行為觀察")

col_obs1, col_obs2 = st.columns(2)

with col_obs1:
    # 1. 選擇觀察時機
    st.markdown("#### 1️⃣ 手部衛生時機")
    hand_hygiene_moment = st.radio(
        "請選擇觀察時機",
        [
            "時機1: 接觸病人前",
            "時機2: 執行清潔/無菌操作技術前",
            "時機3: 暴露病人體液風險後",
            "時機4: 接觸病人後",
            "時機5: 接觸病人周遭環境後"
        ],
        key="hand_hygiene_moment",
        label_visibility="collapsed"
    )

with col_obs2:
    # 2. 選擇手部衛生執行方式
    st.markdown("#### 2️⃣ 執行方式")
    hygiene_method = st.radio(
        "請選擇執行方式",
        ["乾洗手（酒精性乾洗手液）", "濕洗手（肥皂和水）", "沒有洗手"],
        key="hygiene_method",
        label_visibility="collapsed"
    )

# 初始化變數
technique_correct = None
incorrect_reason = None

if hygiene_method != "沒有洗手":
    st.markdown("---")
    st.markdown("#### 3️⃣ 正確性評估")
    
    col_correct1, col_correct2 = st.columns([1, 2])
    
    with col_correct1:
        technique_correct = st.radio(
            "執行正確性",
            ["正確(七步驟完全正確)", "不正確"],
            key="technique_correct"
        )
    
    with col_correct2:
        if technique_correct == "不正確":
            # 根據乾洗手或濕洗手顯示不同的不正確原因（支援複選）
            if hygiene_method == "乾洗手（酒精性乾洗手液）":
                incorrect_options = ["步驟不完整", "戴手套洗手", "搓揉時間過短(少於20-30秒)或未搓到全乾", 
                                    "乾洗手液量不足"]
            else:  # 濕洗手
                incorrect_options = ["步驟不完整", "戴手套洗手", "未使用洗手劑(含肥皂)洗手", 
                                    "洗手後未擦乾", "洗手時間過短(少於40-60秒)"]
            
            st.write("**不正確原因（可複選）**")
            selected_reasons = []
            
            # 使用 checkbox 顯示所有選項
            for option in incorrect_options:
                if st.checkbox(option, key=f"incorrect_{option}"):
                    selected_reasons.append(option)
            
            # 「其他」選項
            other_checked = st.checkbox("其他(請註明)", key="incorrect_other_checkbox")
            if other_checked:
                other_reason = st.text_input("請註明原因", key="incorrect_reason_other")
                if other_reason:
                    selected_reasons.append(other_reason)
            
            # 將複選結果合併為字串
            incorrect_reason = ", ".join(selected_reasons) if selected_reasons else None
        else:
            incorrect_reason = None

# 備註
st.markdown("---")
notes = st.text_area("💬 備註（選填）", placeholder="請填寫其他觀察事項", height=60, key="notes")

# 提交和結束按鈕
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("✅ 提交此次觀察", type="primary", use_container_width=True):
        # 驗證必填欄位
        if not auditor:
            st.error("請填寫稽核人員姓名！")
        elif hygiene_method != "沒有洗手" and not technique_correct:
            st.error("請評估執行正確性！")
        elif technique_correct == "不正確" and not incorrect_reason:
            st.error("請選擇不正確原因！")
        else:
            # 創建觀察記錄
            # 使用台灣時區（UTC+8）
            taiwan_tz = timezone(timedelta(hours=8))
            now_taiwan = datetime.now(taiwan_tz)
            observation = {
                "登入者Email": st.session_state.user_email,
                "稽核日期": now_taiwan.strftime("%Y-%m-%d"),
                "稽核時間": now_taiwan.strftime("%H:%M:%S"),
                "稽核列計月份": audit_month,
                "稽核者單位": st.session_state.department,
                "稽核人員": st.session_state.auditor,
                "受稽核人員類別": st.session_state.staff_category,
                "受稽核者單位": st.session_state.staff_unit,
                "手部衛生時機": hand_hygiene_moment,
                "手部衛生方式": hygiene_method,
                "手部衛生正確性": technique_correct if hygiene_method != "沒有洗手" else "未評估(沒有洗手)",
                "不正確原因": incorrect_reason if incorrect_reason else "無"
            }
            
            # 保存到 Google Sheets
            with st.spinner("正在保存到雲端..."):
                if save_to_google_sheets(observation, audit_month):
                    st.session_state.latest_monthly_record = observation
                    st.session_state.latest_monthly_record_key = f"{st.session_state.user_email}|{audit_month}"
                    st.session_state.monthly_history_records.append(observation)
                    st.session_state.monthly_history_records = sorted(
                        st.session_state.monthly_history_records,
                        key=lambda record: datetime.strptime(
                            f"{record.get('稽核日期', '')} {record.get('稽核時間', '00:00:00')}",
                            "%Y-%m-%d %H:%M:%S",
                        ),
                    )
                    st.session_state.current_observations.append(observation)
                    st.success("✅ 觀察記錄已成功保存！")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ 保存失敗，請檢查網路連接")

with col2:
    if st.button("🏁 結束觀察", type="secondary", use_container_width=True):
        # 重置所有狀態
        st.session_state.audit_month = ""
        st.session_state.auditor = ""
        st.session_state.department = "ER"
        st.session_state.staff_category = "護理師"
        st.session_state.current_observations = []
        st.success("稽核已結束，可以開始新的稽核。")
        st.rerun()

# 顯示本月填報報表
report_records = st.session_state.get("monthly_history_records", [])
if report_records:
    st.markdown("---")
    st.subheader("📊 稽核統計報表")

    df_current = pd.DataFrame(report_records)

    def month_sort_key(month_text):
        month_text = str(month_text).strip()
        digits = "".join(ch for ch in month_text if ch.isdigit())
        return int(digits) if digits else 99

    has_new_month_column = "稽核列計月份" in df_current.columns
    has_legacy_month_column = "稽核月份" in df_current.columns

    if has_new_month_column or has_legacy_month_column:
        normalized_month_column = "稽核列計月份_顯示"

        if has_new_month_column and has_legacy_month_column:
            merged_month_series = df_current["稽核列計月份"].where(
                df_current["稽核列計月份"].notna() & (df_current["稽核列計月份"].astype(str).str.strip() != ""),
                df_current["稽核月份"],
            )
        elif has_new_month_column:
            merged_month_series = df_current["稽核列計月份"]
        else:
            merged_month_series = df_current["稽核月份"]

        df_current[normalized_month_column] = merged_month_series.fillna("未填").astype(str).replace({"": "未填", "None": "未填", "nan": "未填"})

        month_groups = df_current.groupby(normalized_month_column, dropna=False)
        sorted_months = sorted(
            month_groups.groups.keys(),
            key=lambda month_text: month_sort_key(month_text) if month_text != "未填" else 999,
        )

        for month_name in sorted_months:
            month_df = month_groups.get_group(month_name).copy()
            month_total = len(month_df)
            month_staff_counts = month_df["受稽核人員類別"].value_counts().to_dict()
            month_staff_summary = " | ".join([f"{staff}: {count}次" for staff, count in month_staff_counts.items()])

            st.markdown(f"### {month_name}")
            st.markdown(f"- **{month_name}稽核次數：** 總稽核次數{month_total}次")
            st.markdown(f"- **{month_name}各受稽人員次數：** {month_staff_summary if month_staff_summary else '無資料'}")

        st.markdown("---")
        st.markdown("### 明細列表")

        display_columns = [
            normalized_month_column,
            "稽核日期",
            "稽核時間",
            "稽核者單位",
            "稽核人員",
            "受稽核人員類別",
            "受稽核者單位",
            "手部衛生時機",
            "手部衛生方式",
            "手部衛生正確性",
            "不正確原因",
        ]
        display_columns = [column for column in display_columns if column in df_current.columns]
        report_display = df_current[display_columns].copy()
        report_display.rename(
            columns={
                normalized_month_column: "稽核列計月份",
                "稽核時間": "時間",
                "稽核人員": "稽核者人員",
            },
            inplace=True,
        )
        report_display.insert(0, "序", range(1, len(report_display) + 1))

        st.dataframe(
            report_display,
            use_container_width=True,
            height=min(520, 50 + len(report_display) * 35),
            hide_index=True,
        )
    else:
        st.info("目前資料缺少稽核列計月份欄位，無法依月份統計。")

# 頁尾
st.markdown("---")
st.caption("手部衛生稽核系統 v3.0 | 數據同步至 Google 雲端")
