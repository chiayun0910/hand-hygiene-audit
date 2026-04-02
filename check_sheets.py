"""檢查 Google Sheets 目前狀態"""
import gspread

# 連接到 Google Sheets
gc = gspread.service_account(filename='key.json')
spreadsheet = gc.open("hand-hygiene-new")

# 列出所有工作表
worksheets = spreadsheet.worksheets()
print("📊 目前 Google Sheet 的工作表：")
print("=" * 50)
for idx, ws in enumerate(worksheets, 1):
    all_values = ws.get_all_values()
    row_count = len(all_values)
    data_count = row_count - 1 if row_count > 1 else 0  # 扣除標題行
    
    print(f"\n{idx}. 工作表名稱：{ws.title}")
    print(f"   總列數：{row_count}")
    print(f"   資料筆數：{data_count}")
    
    if row_count > 1:
        print(f"   ⚠️  包含測試資料")
    else:
        print(f"   ✅ 無測試資料")

print("\n" + "=" * 50)
print(f"✅ 檢查完成！共有 {len(worksheets)} 個工作表")
