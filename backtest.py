import yfinance as yf
import pandas as pd
import os

VOL_MULTIPLE = 1.5
LOOKBACK_DAYS = 90
BATCH = 100

# 直接讀你圖入面嗰個tickers.txt (611隻)
if os.path.exists("tickers.txt"):
    with open("tickers.txt","r") as f:
        TICKERS = [l.strip() for l in f if l.strip() and not l.startswith("...")]
else:
    TICKERS = ["AAPL","MSFT","NVDA","TSLA","SPCX","RKLB","PLTR"]

# 去重
TICKERS = list(dict.fromkeys(TICKERS))
print(f"回測：取消第4條>55W | {len(TICKERS)}隻 | {LOOKBACK_DAYS}日 | 分{BATCH}隻一批")

all_hits=[]
for i in range(0, len(TICKERS), BATCH):
    batch = TICKERS[i:i+BATCH]
    print(f"批次 {i//BATCH+1}/{(len(TICKERS)-1)//BATCH+1}: {batch[0]}...{batch[-1]}")
    try:
        data = yf.download(batch, period="1y", group_by='ticker', threads=True, auto_adjust=True, progress=False)
        for ticker in batch:
            try:
                df = data[ticker] if len(batch)>1 else data
                if len(df) < 100: continue
                df['MA20'] = df['Close'].rolling(20).mean()
                df['Vol_MA20'] = df['Volume'].rolling(20).mean()
                for k in range(-LOOKBACK_DAYS, -1):
                    last=df.iloc[k]; prev=df.iloc[k-1]
                    ma20_now=df['MA20'].iloc[k]; ma20_5=df['MA20'].iloc[k-5]
                    vol_ma=df['Vol_MA20'].iloc[k]
                    if pd.isna(ma20_now) or pd.isna(vol_ma): continue
                    # 取消第4條
                    cond1 = last['Close'] < ma20_now and (ma20_now - ma20_5 < 0)
                    cond2 = prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Open'] < prev['Close'] and last['Close'] > prev['Open']
                    cond3 = last['Volume'] > vol_ma * VOL_MULTIPLE
                    cond4 = True
                    if cond1 and cond2 and cond3 and cond4:
                        all_hits.append(f"{df.index[k].strftime('%Y-%m-%d')} {ticker} 收{last['Close']:.2f} 量{last['Volume']/vol_ma:.1f}x")
            except: continue
    except Exception as e:
        print(f"批次失敗跳過: {e}")
        continue

all_hits.sort()
print("\n".join(all_hits) if all_hits else "取消55W後都係0隻")
print(f"\n總共 {len(all_hits)} 次觸發 / {len(TICKERS)}隻掃描")