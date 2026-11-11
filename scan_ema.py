import yfinance as yf
import pandas as pd
import requests
import os

# 讀股票池 - 同你之前一樣
with open('tickers.txt') as f:
    tickers = [t.strip() for t in f if t.strip()]

results = []
for t in tickers:
    try:
        df = yf.download(t, period="3mo", interval="1d", progress=False, auto_adjust=True)
        if len(df) < 30:
            continue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        close = df['Close']
        vol = df['Volume']
        
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema25 = close.ewm(span=25, adjust=False).mean()
        
        # 條件1: 量 > 1.5倍
        avg_vol = vol.iloc[-21:-1].mean()
        vol_ratio = vol.iloc[-1] / avg_vol if avg_vol > 0 else 0
        
        # 條件2: 金叉 - 琴日仲喺下面，今日升穿
        cross = (ema12.iloc[-2] < ema25.iloc[-2]) and (ema12.iloc[-1] > ema25.iloc[-1])
        
        if vol_ratio > 1.5 and cross:
            results.append({
                'Ticker': t,
                'Close': round(float(close.iloc[-1]), 2),
                'EMA12': round(float(ema12.iloc[-1]), 2),
                'EMA25': round(float(ema25.iloc[-1]), 2),
                'Vol_Ratio': round(float(vol_ratio), 2),
                'Volume': int(vol.iloc[-1])
            })
    except Exception as e:
        print(f"{t} error: {e}")
        continue

# 寫 history
df_out = pd.DataFrame(results)
df_out.to_csv('ema_triggers_history.csv', index=False)

msg = f"🚀 EMA金叉觸發 ({len(results)}隻)\n"
if len(results) == 0:
    msg += "今日無觸發"
else:
    for _, r in df_out.sort_values('Vol_Ratio', ascending=False).iterrows():
        msg += f"\n{r['Ticker']} {r['Close']:.2f} 量{r['Vol_Ratio']:.2f}x EMA12 {r['EMA12']:.2f} > {r['EMA25']:.2f}"

print(msg)

# WhatsApp 同你之前一樣
phone = os.environ.get('CALLMEBOT_PHONE')
apikey = os.environ.get('CALLMEBOT_APIKEY')
if phone and apikey:
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={requests.utils.quote(msg)}&apikey={apikey}"
    requests.get(url)