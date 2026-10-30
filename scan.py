# scan.py - 自動累積版
import os, yfinance as yf, pandas as pd, requests
from datetime import datetime

TICKER_FILE = "tickers.txt"
HISTORY_FILE = "triggers_history.csv"
STOP_FACTOR = 0.98

def is_triggered(df):
    if len(df) < 30:
        return False, None, None
    close = float(df['Close'].iloc[-1])
    low = float(df['Low'].iloc[-1])
    prev_high = float(df['High'].iloc[-21:-1].max())
    vol = float(df['Volume'].iloc[-1])
    avg_vol = float(df['Volume'].iloc[-21:-1].mean())
    triggered = (close > prev_high) and (vol > avg_vol * 1.2)
    return triggered, close, low

def send_whatsapp(msg):
    token = os.getenv("ULTRA_TOKEN")
    instance = os.getenv("ULTRA_INSTANCE")
    to = os.getenv("TO_NUMBER", "")
    if not token or not instance or not to:
        print(msg)
        return
    url = f"https://api.ultramsg.com/{instance}/messages/chat"
    try:
        requests.post(url, data={"token": token, "to": to, "body": msg}, timeout=20)
    except Exception as e:
        print(f"Send fail {e}")

def main():
    with open(TICKER_FILE) as f:
        tickers = [x.strip() for x in f if x.strip()]

    today = datetime.now().strftime("%Y-%m-%d")
    new_alerts = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="3mo", auto_adjust=True, progress=False, group_by='column')
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            triggered, close, low = is_triggered(df)
            if triggered:
                new_alerts.append([today, ticker, close, low, low*STOP_FACTOR])
                send_whatsapp(f"🚀 {ticker} 觸發 ${close:.2f} | 止損 ${low*STOP_FACTOR:.2f} | T+2開市買")
        except: continue

    # --- 自動累積邏輯 ---
    cols = ["date","ticker","close","low_raw","stop_98"]
    if os.path.exists(HISTORY_FILE):
        hist = pd.read_csv(HISTORY_FILE)
    else:
        # 第一次用你46隻做底
        initial = [
            ["2026-06-26","FMC"],["2026-07-23","WYNN"],["2026-07-28","GRAB"],["2026-07-29","CHRW"],
            ["2026-08-04","CE"],["2026-08-04","CTVA"],["2026-08-04","WMB"],["2026-08-06","SPCX"],
            ["2026-08-11","FHN"],["2026-08-17","BIDU"],["2026-08-25","TME"],["2026-08-26","OKTA"],
            ["2026-08-31","ALGN"],["2026-09-08","FRT"],["2026-09-08","XEL"],["2026-09-16","AXON"],
            ["2026-09-18","0083.HK"],["2026-09-18","0288.HK"],["2026-09-18","BKR"],["2026-09-18","DAL"],
            ["2026-09-18","DRI"],["2026-09-18","MAR"],["2026-09-18","MCO"],["2026-09-18","MMM"],
            ["2026-09-18","PH"],["2026-09-18","PRU"],["2026-09-18","TSN"],["2026-09-21","1109.HK"],
            ["2026-09-29","CMS"],["2026-09-29","DTE"],["2026-09-29","EXC"],["2026-09-29","LNT"],
            ["2026-09-29","PNW"],["2026-09-29","SO"],["2026-10-01","BA"],["2026-10-01","NEE"],
            ["2026-10-02","EFX"],["2026-10-02","LW"],["2026-10-05","MDT"],["2026-10-06","DHI"],
            ["2026-10-15","IONQ"],["2026-10-15","NXPI"],["2026-10-20","LCID"],["2026-10-20","UAL"],
            ["2026-10-22","ALK"],["2026-10-23","MOS"],
        ]
        hist = pd.DataFrame(initial, columns=["date","ticker"])
        hist["close"]=0; hist["low_raw"]=0; hist["stop_98"]=0
        hist = hist[cols]

    if new_alerts:
        new_df = pd.DataFrame(new_alerts, columns=cols)
        hist = pd.concat([hist, new_df], ignore_index=True)
        hist.drop_duplicates(subset=["date","ticker"], keep="last", inplace=True)
    
    hist.to_csv(HISTORY_FILE, index=False)
    print(f"History now {len(hist)} rockets")

if __name__ == "__main__":
    main()