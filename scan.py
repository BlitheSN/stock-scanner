import yfinance as yf
import pandas as pd
import os
import requests
from datetime import datetime

HISTORY_US = "triggers_history.csv"
HISTORY_HK = "hk_triggers_history.csv"
TICKERS_FILE = "tickers.txt"

def get_us_tickers():
    # 1. 優先用你tickers.txt入面嗰611隻
    if os.path.exists(TICKERS_FILE):
        try:
            with open(TICKERS_FILE, "r") as f:
                tickers = [line.strip() for line in f if line.strip()]
                if len(tickers) > 100:
                    print(f"用 tickers.txt: {len(tickers)}隻")
                    return tickers
        except: pass
    # 2. 冇就抓S&P500
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        table = pd.read_html(url)[0]
        tickers = table['Symbol'].str.replace('.', '-', regex=False).tolist()
        print(f"用 S&P500: {len(tickers)}隻")
        return tickers
    except:
        return ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","MGM","LVS"]

US_TICKERS = get_us_tickers()
HK_TICKERS = ["0700.HK","0005.HK","0941.HK","0939.HK","1398.HK","1299.HK","2318.HK","0388.HK","0883.HK","0857.HK","2628.HK","3968.HK","2319.HK","0011.HK","2388.HK","0006.HK","0003.HK","0002.HK","1038.HK","0001.HK","0016.HK","1019.HK","1109.HK","1209.HK","1997.HK","0960.HK","1093.HK","2269.HK","3690.HK","1810.HK","9988.HK","9618.HK","1024.HK","9888.HK","9999.HK","2015.HK","1818.HK","0288.HK","0358.HK","0669.HK","1211.HK","0175.HK","0968.HK","2020.HK","2313.HK","0291.HK","0661.HK","1177.HK","2018.HK","2800.HK","2382.HK","1347.HK","0267.HK","1928.HK"]
HK_TICKERS = list(dict.fromkeys(HK_TICKERS))

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
    token = os.getenv("ULTRA_TOKEN")
    instance = os.getenv("ULTRA_INSTANCE")
    to = os.getenv("TO_NUMBER")
    if not token or not instance or not to: print("Missing secrets"); return
    url = f"https://api.ultramsg.com/{instance}/messages/chat"
    data = {"token": token, "to": to, "body": msg}
    r = requests.post(url, data=data)
    print(r.text)

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
msg += f"掃描數: 美股{len(US_TICKERS)}隻 + 港股{len(HK_TICKERS)}隻\n\n"
msg += f"🇺🇸 美股觸發: {len(us_new)}隻\n" + ("\n".join([f"{x[1]} 收:{x[2]}" for x in us_new]) if us_new else "今日0隻") + "\n\n"
msg += f"🇭🇰 港股觸發: {len(hk_new)}隻 (市值>200億)\n" + ("\n".join([f"{x[1]} 收:{x[2]}" for x in hk_new]) if hk_new else "今日0隻")

print(msg)
send_whatsapp(msg)