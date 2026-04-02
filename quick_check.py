#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import pandas as pd

try:
    print("開始讀取檔案...")
    df = pd.read_excel("hand-hygiene.xlsx", engine='openpyxl')
    print(f"成功讀取! 共 {len(df)} 筆資料")
    print("\n欄位:", list(df.columns))
    
    if '時機' in df.columns:
        print("\n時機統計:")
        print(df['時機'].value_counts().sort_index())
    
    print("\n前5筆資料:")
    print(df.head())
    
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
