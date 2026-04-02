import pandas as pd
import os

# 讀取 Excel 檔案
file_path = "hand-hygiene.xlsx"
print(f"正在分析: {file_path}")
print("=" * 60)

try:
    df = pd.read_excel(file_path)
    
    # 基本資訊
    print(f"\n📊 基本資訊:")
    print(f"   總筆數: {len(df)}")
    print(f"   欄位數: {len(df.columns)}")
    print(f"   檔案大小: {os.path.getsize(file_path) / 1024:.2f} KB")
    
    # 欄位名稱
    print(f"\n📋 欄位名稱:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")
    
    # 顯示前幾筆資料
    print(f"\n📝 前 10 筆資料:")
    print(df.head(10).to_string())
    
    # 時機數統計
    if '時機' in df.columns:
        print(f"\n⏱️  時機數統計:")
        timing_counts = df['時機'].value_counts().sort_index()
        for timing, count in timing_counts.items():
            percentage = (count / len(df)) * 100
            print(f"   時機 {timing}: {count} 筆 ({percentage:.1f}%)")
        
        # 檢查是否有五個時機
        expected_timings = [1, 2, 3, 4, 5]
        missing_timings = [t for t in expected_timings if t not in timing_counts.index]
        if missing_timings:
            print(f"\n⚠️  缺少的時機: {missing_timings}")
        else:
            print(f"\n✅ 五個時機都有資料")
    else:
        print(f"\n⚠️  找不到「時機」欄位")
    
    # 其他統計
    if '是否落實' in df.columns:
        print(f"\n✋ 落實情況統計:")
        compliance = df['是否落實'].value_counts()
        for status, count in compliance.items():
            percentage = (count / len(df)) * 100
            print(f"   {status}: {count} 筆 ({percentage:.1f}%)")
    
    if '科別' in df.columns:
        print(f"\n🏥 科別統計:")
        dept_counts = df['科別'].value_counts()
        for dept, count in dept_counts.head(10).items():
            percentage = (count / len(df)) * 100
            print(f"   {dept}: {count} 筆 ({percentage:.1f}%)")
    
    if '單位' in df.columns:
        print(f"\n🏢 單位統計:")
        unit_counts = df['單位'].value_counts()
        for unit, count in unit_counts.head(10).items():
            percentage = (count / len(df)) * 100
            print(f"   {unit}: {count} 筆 ({percentage:.1f}%)")
    
    if '日期' in df.columns:
        print(f"\n📅 日期範圍:")
        df['日期'] = pd.to_datetime(df['日期'])
        print(f"   最早: {df['日期'].min()}")
        print(f"   最晚: {df['日期'].max()}")
        print(f"   天數: {(df['日期'].max() - df['日期'].min()).days + 1} 天")

except FileNotFoundError:
    print(f"❌ 找不到檔案: {file_path}")
except Exception as e:
    print(f"❌ 發生錯誤: {str(e)}")
    import traceback
    traceback.print_exc()
