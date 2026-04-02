"""自動清除 Google Sheets 測試數據"""
import gspread

# 連接到 Google Sheets
gc = gspread.service_account(filename='key.json')
spreadsheet = gc.open("hand-hygiene-new")

# 列出所有工作表
worksheets = spreadsheet.worksheets()
print("📊 目前的工作表：")
for idx, ws in enumerate(worksheets, 1):
    row_count = len(ws.get_all_values())
    print(f"  {idx}. {ws.title} ({row_count} 列資料)")

# 自動刪除所有測試工作表（保留工作表1）
deleted_count = 0
for ws in worksheets:
    if ws.title != "工作表1":
        print(f"\n🗑️  刪除工作表：{ws.title}")
        
        # 先清空資料
        try:
            all_values = ws.get_all_values()
            if len(all_values) > 1:  # 如果有資料行（除了標題）
                # 刪除所有資料行，保留標題
                ws.delete_rows(2, len(all_values))
                print(f"   ✅ 已清空 {len(all_values)-1} 列資料")
            else:
                print(f"   ℹ️  工作表已是空的")
        except Exception as e:
            print(f"   ⚠️  清空資料時發生錯誤：{str(e)}")
        
        # 然後刪除工作表
        try:
            spreadsheet.del_worksheet(ws)
            print(f"   ✅ 已刪除工作表")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ 刪除工作表時發生錯誤：{str(e)}")

print(f"\n✅ 完成！共刪除 {deleted_count} 個測試工作表")
