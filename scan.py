import yfinance as yf
import pandas as pd
import os
from datetime import datetime

TICKER_FILE = "tickers.txt"
HISTORY_FILE = "triggers_history.csv"
VOL_MULTIPLE = 1.5

def is_triggered(df):
    if len(df) < 30:
        return False, None, None
    df['MA20'] = df['Close'].rolling(20).mean()
    df['Vol_MA20'] = df['Volume'].rolling(20).mean()
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    ma20_now = df['MA20'].iloc[-1]
    ma20_5 = df['MA20'].iloc[-6]  # 5日前
    
    if pd.isna(ma20_now) or pd.isna(ma20_5):
        return False, None, None

    cond1 = last['Close'] < ma20_now and (ma20_now - ma20_5 < 0)
    cond2 = prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Open'] < prev['Close'] and last['Close'] > prev['Open']
    cond3 = last['Volume'] > df['Vol_MA20'].iloc[-1] * VOL_MULTIPLE

    triggered = cond1 and cond2 and cond3
    return triggered, float(last['Close']), float(last['Low'])

def main():
    tickers = [t.strip() for t in open(TICKER_FILE).read().splitlines() if t.strip()]
    today = datetime.now().strftime("%Y-%m-%d")
    new_rows = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="3mo", progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            ok, close, low = is_triggered(df)
            if ok:
                new_rows.append([today, ticker, close, low])
                print(f"TRIGGER {ticker}")
        except Exception as e:
            continue

    if os.path.exists(HISTORY_FILE):
        hist = pd.read_csv(HISTORY_FILE)
    else:
        hist = pd.read_csv("initial_46.csv") if os.path.exists("initial_46.csv") else pd.DataFrame(columns=["date","ticker","close","low"])

    if new_rows:
        new_df = pd.DataFrame(new_rows, columns=["date","ticker","close","low"])
        hist = pd.concat([hist, new_df]).drop_duplicates(subset=["date","ticker"], keep="last")
        hist.to_csv(HISTORY_FILE, index=False)
        print(f"Added {len(new_rows)}")

if __name__ == "__main__":
    main()