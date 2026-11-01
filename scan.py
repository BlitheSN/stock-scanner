import yfinance as yf
import pandas as pd
import os
import requests
import urllib.parse
from datetime import datetime

HISTORY_US = "triggers_history.csv"
HISTORY_HK = "hk_triggers_history.csv"
TICKERS_FILE = "tickers.txt"

def get_us_tickers():
    with open(TICKERS_FILE, "r") as f:
        tickers = [line.strip() for line in f if line.strip()]
    print(f"鎖定 tickers.txt: {len(tickers)}隻")
    return tickers

US_TICKERS = get_us_tickers()
HK_TICKERS = [t for t in US_TICKERS if t.endswith(".HK")]
US_TICKERS = [t for t in US_TICKERS if not t.endswith(".HK")]

def check_trigger(df):
    if len(df) < 25: return False,0,0
    close = df['Close'].iloc[-1]
    low = df['Low'].iloc[-1]
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    ma20_prev = df['Close'].rolling(20).mean().iloc[-2]
    cond1 = close < ma20 and ma20 < ma20_prev
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    cond2 = prev['Close'] < prev['Open'] and curr['Close'] > curr['Open'] and curr['Close'] > prev['Open'] and curr['Open'] < prev['Close']
    vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
    cond3 = df['Volume'].iloc[-1] > vol_ma * 1.5 if vol_ma else False
    return cond1 and cond2 and cond3, close, low

def send_whatsapp(msg):
    phone = os.getenv("CALLMEBOT_PHONE")
    apikey = os.getenv("CALLMEBOT_APIKEY")
    if not phone or not apikey: return
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={urllib.parse.quote(msg)}&apikey={apikey}"
    try: requests.get(url, timeout=20)
    except: pass

def scan_list(tickers, is_hk=False):
    new_rows = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="100d")
            if df.empty or len(df) < 25: continue
            if is_hk:
                try:
                    mcap = stock.info.get('marketCap',0) or 0
                    if mcap and mcap < 20000000000: continue
                except: pass
            ok, c, l = check_trigger(df)
            if ok:
                new_rows.append([datetime.now().strftime("%Y-%m-%d"), ticker, round(float(c),2), round(float(l),2)])
        except: continue
    return new_rows

us_new = scan_list(US_TICKERS, is_hk=False)
hk_new = scan_list(HK_TICKERS, is_hk=True)

for file, rows in [(HISTORY_US, us_new), (HISTORY_HK, hk_new)]:
    if rows:
        df_new = pd.DataFrame(rows, columns=["date","ticker","close","low"])
        df_all = pd.concat([pd.read_csv(file), df_new], ignore_index=True) if os.path.exists(file) else df_new
        df_all.to_csv(file, index=False)

msg = f"📊 掃描結果 {datetime.now().strftime('%Y-%m-%d %H:%M HKT')}\n"
msg += f"掃描數: 美股{len(US_TICKERS)}隻 + 港股{len(HK_TICKERS)}隻 = {len(US_TICKERS)+len(HK_TICKERS)}隻 (已鎖定)\n\n"
msg += f"🇺🇸 美股觸發: {len(us_new)}隻\n" + ("\n".join([f"{x[1]} 收:{x[2]}" for x in us_new]) if us_new else "今日0隻") + "\n\n"
msg += f"🇭🇰 港股觸發: {len(hk_new)}隻\n" + ("\n".join([f"{x[1]} 收:{x[2]}" for x in hk_new]) if hk_new else "今日0隻")

print(msg)
send_whatsapp(msg)