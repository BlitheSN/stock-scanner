import yfinance as yf
import pandas as pd
import os

VOL_MULTIPLE = 1.5
LOOKBACK_DAYS = 90  # 先睇90日

if os.path.exists("tickers.txt"):
    with open("tickers.txt","r") as f:
        TICKERS = [l.strip() for l in f if l.strip()]
else:
    TICKERS = ["AAPL","MSFT","NVDA","TSLA","ORCL","ENTG","HCA","IEX","SPCX","RKLB","PLTR"]

print(f"回測模式：取消第4條55W | {len(TICKERS)}隻 | {LOOKBACK_DAYS}日")

data = yf.download(TICKERS, period="1y", group_by='ticker', threads=True, auto_adjust=True, progress=False)

all_hits=[]
for ticker in TICKERS:
    try:
        df = data[ticker] if len(TICKERS)>1 else data
        if len(df) < 100: continue
        df['MA20'] = df['Close'].rolling(20).mean()
        df['Vol_MA20'] = df['Volume'].rolling(20).mean()
        for i in range(-LOOKBACK_DAYS, -1):
            last=df.iloc[i]; prev=df.iloc[i-1]
            ma20_now=df['MA20'].iloc[i]; ma20_5=df['MA20'].iloc[i-5]
            vol_ma=df['Vol_MA20'].iloc[i]
            if pd.isna(ma20_now): continue
            
            # 保留3條，取消第4條
            cond1 = last['Close'] < ma20_now and (ma20_now - ma20_5 < 0)
            cond2 = prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Open'] < prev['Close'] and last['Close'] > prev['Open']
            cond3 = last['Volume'] > vol_ma * VOL_MULTIPLE
            cond4 = True  # <--- 第4條取消

            if cond1 and cond2 and cond3 and cond4:
                all_hits.append(f"{df.index[i].strftime('%Y-%m-%d')} {ticker} 收{last['Close']:.2f} 量{last['Volume']/vol_ma:.1f}x")
    except: continue

all_hits.sort()
print("\n".join(all_hits) if all_hits else "取消55W後都係0隻 - 代表第1條MA20向下都好嚴")
print(f"\n總共 {len(all_hits)} 次觸發")