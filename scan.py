import yfinance as yf, mplfinance as mpf, requests, os, time
from datetime import datetime
INSTANCE_ID = os.getenv("ULTRA_INSTANCE")
TOKEN = os.getenv("ULTRA_TOKEN")
PHONE = "85252871318"
VOL_MULTIPLE = 1.8
HK = ["0700.HK","0005.HK","0941.HK","1299.HK","1810.HK","09988.HK","1024.HK","3690.HK","2800.HK","0388.HK","2318.HK"]
US = ["AAPL","MSFT","NVDA","TSLA","GOOGL","META","AMZN","NFLX","SPY","QQQ"]
def send(msg, img=None):
    base = f"https://api.ultramsg.com/{INSTANCE_ID}/messages"
    requests.post(f"{base}/chat", data={"token": TOKEN, "to": PHONE, "body": msg}, timeout=20)
    if img and os.path.exists(img):
        with open(img, 'rb') as f:
            requests.post(f"{base}/image", data={"token": TOKEN, "to": PHONE, "caption": msg}, files={"image": f}, timeout=20)
def scan(t):
    try:
        df = yf.Ticker(t).history(period="2y", auto_adjust=True)
        if len(df)<300: return None
        df['MA20']=df['Close'].rolling(20).mean(); df['MA20_slope']=df['MA20'].diff(5); df['Vol_MA20']=df['Volume'].rolling(20).mean()
        weekly=df['Close'].resample('W').last(); df['WMA55']=weekly.rolling(55).mean().reindex(df.index, method='ffill')
        last, prev = df.iloc[-1], df.iloc[-2]
        ok = (last['Close']<last['MA20'] and last['MA20_slope']<0 and prev['Close']<prev['Open'] and last['Close']>last['Open'] and last['Open']<prev['Close'] and last['Close']>prev['Open'] and last['Volume']>last['Vol_MA20']*VOL_MULTIPLE and last['Close']>last['WMA55'])
        if ok:
            img=f"/tmp/{t.replace('.','_')}.png"; mpf.plot(df.tail(90), type='candle', mav=20, volume=True, title=f"{t} {last['Close']:.2f}", style='yahoo', savefig=dict(fname=img, dpi=100)); return img, last
    except: return None
now=datetime.now().strftime("%m/%d %H:%M"); send(f"🔍 {now} 自動掃描開始..."); hits=0
for t in HK+US:
    r=scan(t)
    if r:
        img,last=r; send(f"✅ {t}\n下跌中陽包陰+放量{last['Volume']/last['Vol_MA20']:.1f}x+企55W\n現價 {last['Close']:.2f}", img); hits+=1; time.sleep(2)
if hits==0: send(f"📭 {now} 今日無符合")
