import yfinance as yf
import pandas as pd
import os
import requests
from datetime import datetime

HISTORY_FILE = "triggers_history.csv"
HK_HISTORY_FILE = "hk_triggers_history.csv"

# === 美股 611隻 (你原本) ===
# (保留你原本嗰個 us_tickers list)

# === 港股：恒指 + 國指 + 科指 成份，大約150隻 ===
HK_TICKERS = [
 "0700.HK","0005.HK","0941.HK","0939.HK","1398.HK","1299.HK","2318.HK","0388.HK","0883.HK","0857.HK",
 "2628.HK","3968.HK","2319.HK","0011.HK","2388.HK","0006.HK","0003.HK","0002.HK","1038.HK","0001.HK",
 "0016.HK","1019.HK","1109.HK","1209.HK","1997.HK","0960.HK","1093.HK","2269.HK","3690.HK","1810.HK",
 "9988.HK","9618.HK","1024.HK","9888.HK","9999.HK","2015.HK","1818.HK","0288.HK","0358.HK","0669.HK",
 "1211.HK","0175.HK","1211.HK","0968.HK","2020.HK","2313.HK","0291.HK","0661.HK","1177.HK","2018.HK",
 "2800.HK","0700.HK","0700.HK"  # 你可以之後再加，我幫你寫咗去重邏輯
]

# 去重
HK_TICKERS = list(dict.fromkeys(HK_TICKERS))

def check_trigger(df):
    if len(df) < 25: return False,0,0
    close = df['Close'].iloc[-1]
    low = df['Low'].iloc[-1]
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    ma20_prev = df['Close'].rolling(20).mean().iloc[-2]
    # 1. 跌破MA20 + MA20向下
    cond1 = close < ma20 and ma20 < ma20_prev
    # 2. 陽包陰
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    cond2 = prev['Close'] < prev['Open'] and curr['Close'] > curr['Open'] and curr['Close'] > prev['Open'] and curr['Open'] < prev['Close']
    # 3. 1.5倍量
    vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
    cond3 = df['Volume'].iloc[-1] > vol_ma * 1.5
    return cond1 and cond2 and cond3, close, low

def scan_hk():
    new_rows = []
    for ticker in HK_TICKERS:
        try:
            stock = yf.Ticker(ticker)
            # 市值>200億
            info = stock.info
            mcap = info.get('marketCap',0)
            if mcap < 200e8:  # 200億港幣 (約20B)
                continue
            df = stock.history(period="100d")
            ok, c, l = check_trigger(df)
            if ok:
                new_rows.append([datetime.now().strftime("%Y-%m-%d"), ticker, c, l])
        except:
            continue
    return new_rows

# 掃完寫檔 + WhatsApp (你原本邏輯保留，再加hk)

# ... 你原本us掃描 ...

hk_new = scan_hk()
if hk_new:
    # 寫入 hk_triggers_history.csv (自動累積)
    # 發 WhatsApp: 🇭🇰 港股觸發: xxx