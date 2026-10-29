import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

VOL_MULTIPLE = 1.5
LOOKBACK_DAYS = 90  # 掃過去90日，你可以改做30/180

with open("tickers.txt","r") as f:
    TICKERS = [l.strip() for l in f if l.strip()]

def backtest_ticker(ticker):
    hits = []
    try:
        df = yf.Ticker(ticker).history(period="1y")
        if len(df) < 300:
            return []
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA55W'] = df['Close'].rolling(275).mean()
        df['Vol_MA20'] = df['Volume'].rolling(20).mean()
        
        # 由 -90日 掃到 -2日 (留返最後一日做prev)
        for i in range(-LOOKBACK_DAYS, -1):
            last = df.iloc[i]
            prev = df.iloc[i-1]
            ma20_now = df['MA20'].iloc[i]
            ma20_5d = df['MA20'].iloc[i-5]
            ma55w = df['MA55W'].iloc[i]
            vol_ma = df['Vol_MA20'].iloc[i]
            if pd.isna(ma20_now) or pd.isna(ma55w) or pd.isna(vol_ma):
                continue
            
            cond1 = (last['Close'] < ma20_now) and (ma20_now - ma20_5d < 0)
            cond2 = (prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Open'] < prev['Close'] and last['Close'] > prev['Open'])
            cond3 = last['Volume'] > vol_ma * VOL_MULTIPLE
            cond4 = last['Close'] > ma55w
            
            if cond1 and cond2 and cond3 and cond4:
                date_str = df.index[i].strftime("%Y-%m-%d")
                hits.append(f"{date_str} {ticker} 收{last['Close']:.2f} 放量{last['Volume']/vol_ma:.1f}x")
    except Exception as e:
        pass
    return hits

if __name__ == "__main__":
    all_hits = []
    for t in TICKERS:
        all_hits.extend(backtest_ticker(t))
    
    all_hits.sort()  # 按日期排
    print("\n".join(all_hits) if all_hits else "過去90日0隻中 - 符合你嚴選預期")
    print(f"\n總共 {len(all_hits)} 次觸發")