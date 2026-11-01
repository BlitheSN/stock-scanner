import yfinance as yf
import pandas as pd
import os
import requests
import urllib.parse
from datetime import datetime

HISTORY_FALL_US = "fall_us_history.csv"
HISTORY_FALL_HK = "fall_hk_history.csv"
TICKERS_FILE = "tickers.txt"

def get_us_tickers():
    if os.path.exists(TICKERS_FILE):
        try:
            with open(TICKERS_FILE, "r") as f:
                tickers = [line.strip() for line in f if line.strip()]
                if len(tickers) > 100:
                    return tickers
        except: pass
    try:
        table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        return table['Symbol'].str.replace('.', '-', regex=False).tolist()
    except:
        return ["AAPL","MSFT","NVDA","MGM"]

US_TICKERS = get_us_tickers()
HK_TICKERS = ["0700.HK","0005.HK","0941.HK","3690.HK","1810.HK","9988.HK","1211.HK","0288.HK","0388.HK","2800.HK"]

def check_fall_trigger(df):
    if len(df) < 25: return False,0,0
    close = df['Close'].iloc[-1]
    high = df['High'].iloc[-1]
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    ma20_prev = df['Close'].rolling(20).mean().iloc[-2]
    # 跌版反轉：股價在MA20上 + MA20向上 (升到頂)
    cond1 = close > ma20 and ma20 > ma20_prev
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    # 陰吞陽：前陽後陰
    cond2 = prev['Close'] > prev['Open'] and curr['Close'] < curr['Open'] and curr['Close'] < prev['Open'] and curr['Open'] > prev['Close']
    vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
    cond3 = df['Volume'].iloc[-1] > vol_ma * 1.5 if vol_ma else False
    return cond1 and cond2 and cond3, close, high

def send_whatsapp(msg):
    phone = os.getenv("CALLMEBOT_PHONE")
    apikey = os.getenv("CALLMEBOT_APIKEY")
    if not phone or not apikey: return
    text = urllib.parse.quote(msg)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={text}&apikey={apikey}"
    try: requests.get(url, timeout=20)
    except: pass

def scan_list(tickers):
    new_rows = []
    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(period="100d")
            if df.empty or len(df) < 25: continue
            ok, c, h = check_fall_trigger(df)
            if ok:
                new_rows.append([datetime.now().strftime("%Y-%m-%d"), ticker, round(float(c),2), round(float(h),2)])
        except: continue
    return new_rows

us_new = scan_list(US_TICKERS)
hk_new = scan_list(HK_TICKERS)

for file, rows in [(HISTORY_FALL_US, us_new), (HISTORY_FALL_HK, hk_new)]:
    if rows:
        df_new = pd.DataFrame(rows, columns=["date","ticker","close","high"])
        df_all = pd.concat([pd.read_csv(file), df_new], ignore_index=True) if os.path.exists(file) else df_new
        df_all.to_csv(file, index=False)

msg = f"📉 下跌版掃描 {datetime.now().strftime('%Y-%m-%d %H:%M HKT')}\n"
msg += f"掃描數: 美股{len(US_TICKERS)}隻 + 港股{len(HK_TICKERS)}隻\n\n"
msg += f"🇺🇸 美股頂部風險: {len(us_new)}隻\n" + ("\n".join([f"{x[1]} 收:{x[2]}" for x in us_new]) if us_new else "今日0隻") + "\n\n"
msg += f"🇭🇰 港股頂部風險: {len(hk_new)}隻\n" + ("\n".join([f"{x[1]} 收:{x[2]}" for x in hk_new]) if hk_new else "今日0隻")

print(msg)
send_whatsapp(msg)