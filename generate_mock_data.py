"""生成2025年手部衛生稽核模擬資料"""
import pandas as pd
import random
from datetime import datetime, timedelta
import openpyxl

# 設定隨機種子以確保可重現
random.seed(42)

# 定義選項
departments = ["ER", "HDR", "OPD", "OPD(市區)", "ICU", "RCW", "7W", "8W", "9W", "11W", 
               "內科", "外科", "精神科", "復健科", "放射科", "檢驗科", 
               "松齡1.2區", "松齡3區", "松齡5.6區", "康寧居", "日照"]

staff_categories = ["護理師", "照服員", "傳送/班長", "病房服務員", "內科醫師", "外科醫師",
                   "內科專師", "外科專師", "職能治療", "物理治療", "營養師", "呼吸治療師",
                   "門診助理員", "語言治療師", "社工師", "醫檢師", "放射師", "精神科醫師",
                   "精神科專師", "精神科職能治療", "心理師"]

hygiene_moments = [
    "時機1: 接觸病人前",
    "時機2: 執行清潔/無菌操作技術前",
    "時機3: 暴露病人體液風險後",
    "時機4: 接觸病人後",
    "時機5: 接觸病人周遭環境後"
]

auditors = ["王小明", "李小華", "張美麗", "陳大同", "林淑芬", "黃志明", "吳雅婷", "劉建國"]

def generate_month_data(year, month, target_compliance_rate, target_correctness_rate):
    """生成單月資料"""
    # 每月總次數：1000-1200
    total_count = random.randint(1000, 1200)
    
    # 確保每個單位至少30次
    min_per_dept = 30
    remaining = total_count - (len(departments) * min_per_dept)
    
    # 分配次數給各單位
    dept_counts = {dept: min_per_dept for dept in departments}
    for _ in range(remaining):
        dept = random.choice(departments)
        dept_counts[dept] += 1
    
    records = []
    
    for dept in departments:
        dept_count = dept_counts[dept]
        
        # 為此單位設定遵從率和正確率（確保不低於最低標準）
        dept_compliance = max(0.88, random.uniform(target_compliance_rate - 0.03, target_compliance_rate + 0.03))
        dept_correctness = max(0.90, random.uniform(target_correctness_rate - 0.02, target_correctness_rate + 0.02))
        
        # 計算此單位應有多少次洗手（遵從）和多少次正確
        compliant_count = int(dept_count * dept_compliance)
        non_compliant_count = dept_count - compliant_count
        correct_count = int(compliant_count * dept_correctness)
        incorrect_count = compliant_count - correct_count
        
        # 生成記錄
        for i in range(dept_count):
            # 生成隨機日期
            day = random.randint(1, 28)  # 安全起見用28天
            hour = random.randint(7, 18)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            audit_date = f"{year}-{month:02d}-{day:02d}"
            audit_time = f"{hour:02d}:{minute:02d}:{second:02d}"
            
            # 隨機選擇
            staff_category = random.choice(staff_categories)
            moment = random.choice(hygiene_moments)
            auditor = random.choice(auditors)
            
            # 決定是否遵從（洗手）
            if i < non_compliant_count:
                # 沒有洗手
                hygiene_method = "沒有洗手"
                correctness = "未評估(沒有洗手)"
                incorrect_reason = "無"
            elif i < non_compliant_count + incorrect_count:
                # 洗手但不正確
                hygiene_method = random.choice(["乾洗手（酒精性乾洗手液）", "濕洗手（肥皂和水）"])
                correctness = "不正確"
                
                if hygiene_method == "乾洗手（酒精性乾洗手液）":
                    # 乾洗手不正確原因（可複選，隨機生成1-2個原因）
                    dry_reasons = ["步驟不完整", "戴手套洗手", "未搓到手部全乾", 
                                  "搓揉時間過短(少於20-30秒)", "乾洗手液量不足已覆蓋全手"]
                    num_reasons = random.choices([1, 2], weights=[0.7, 0.3])[0]
                    selected_reasons = random.sample(dry_reasons, num_reasons)
                    incorrect_reason = ", ".join(selected_reasons)
                else:
                    # 濕洗手不正確原因（可複選，隨機生成1-2個原因）
                    wet_reasons = ["步驟不完整", "戴手套洗手", "只用清水洗手", 
                                  "洗手後未擦乾", "洗手時間過短(少於40-60秒)"]
                    num_reasons = random.choices([1, 2], weights=[0.7, 0.3])[0]
                    selected_reasons = random.sample(wet_reasons, num_reasons)
                    incorrect_reason = ", ".join(selected_reasons)
            else:
                # 洗手且正確
                hygiene_method = random.choice(["乾洗手（酒精性乾洗手液）", "濕洗手（肥皂和水）"])
                correctness = "正確(七步驟完全正確)"
                incorrect_reason = "無"
            
            record = {
                "登入者Email": f"{auditor}@hospital.com",
                "稽核日期": audit_date,
                "稽核時間": audit_time,
                "稽核月份": f"{month}月",
                "稽核者單位": dept,
                "稽核人員": auditor,
                "受稽核人員類別": staff_category,
                "受稽核者單位": dept,  # 簡化：假設都在同一單位
                "手部衛生時機": moment,
                "手部衛生方式": hygiene_method,
                "手部衛生正確性": correctness,
                "不正確原因": incorrect_reason
            }
            
            records.append(record)
    
    return records

# 生成2025年全年資料
print("🔄 開始生成2025年手部衛生稽核模擬資料...")
all_records = []

for month in range(1, 13):
    # 為每月設定目標遵從率和正確率（在範圍內隨機）
    target_compliance = random.uniform(0.920, 0.970)
    target_correctness = random.uniform(0.950, 0.980)
    
    print(f"  ⏳ 生成 {month}月資料（目標遵從率: {target_compliance:.1%}, 正確率: {target_correctness:.1%}）...")
    month_records = generate_month_data(2025, month, target_compliance, target_correctness)
    all_records.extend(month_records)
    
    print(f"  ✅ {month}月完成：{len(month_records)} 筆記錄")

# 創建 DataFrame
df = pd.DataFrame(all_records)

# 輸出為 Excel
output_file = "手部衛生稽核模擬資料_2025年.xlsx"
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"\n✅ 完成！共生成 {len(all_records)} 筆記錄")
print(f"📊 檔案已儲存：{output_file}")

# 計算統計資料
print("\n📈 統計摘要：")
for month in range(1, 13):
    month_df = df[df['稽核月份'] == f"{month}月"]
    total = len(month_df)
    compliant = len(month_df[month_df['手部衛生方式'] != "沒有洗手"])
    correct = len(month_df[month_df['手部衛生正確性'] == "正確(七步驟完全正確)"])
    
    compliance_rate = (compliant / total * 100) if total > 0 else 0
    correctness_rate = (correct / compliant * 100) if compliant > 0 else 0
    
    print(f"  {month}月：{total}次，遵從率 {compliance_rate:.1f}%，正確率 {correctness_rate:.1f}%")

print("\n🎉 模擬資料生成完成！")
