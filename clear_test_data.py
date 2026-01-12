"""清除 Google Sheets 測試數據"""
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

print("\n請輸入要刪除的工作表編號（輸入 0 取消）：")
choice = input("編號: ")

try:
    choice = int(choice)
    if choice == 0:
        print("❌ 已取消")
    elif 1 <= choice <= len(worksheets):
        worksheet = worksheets[choice - 1]
        confirm = input(f"⚠️  確定要刪除「{worksheet.title}」嗎？(y/n): ")
        if confirm.lower() == 'y':
            spreadsheet.del_worksheet(worksheet)
            print(f"✅ 已刪除「{worksheet.title}」工作表")
        else:
            print("❌ 已取消")
    else:
        print("❌ 無效的編號")
except ValueError:
    print("❌ 請輸入數字")
except Exception as e:
    print(f"❌ 錯誤：{str(e)}")

print("\n✅ 完成！")
