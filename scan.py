import yfinance as yf, mplfinance as mpf, requests, os, time, re
from datetime import datetime

INSTANCE_ID = os.getenv("ULTRA_INSTANCE")
TOKEN = os.getenv("ULTRA_TOKEN")
PHONE = "85252871318"
VOL_MULTIPLE = 1.8
HK_CAP = 20_000_000_000 # 200億港元
US_CAP = 10_000_000_000 # 100億美元

def send(msg, img=None):
    base = f"https://api.ultramsg.com/{INSTANCE_ID}/messages"
    requests.post(f"{base}/chat", data={"token": TOKEN, "to": PHONE, "body": msg}, timeout=20)
    if img and os.path.exists(img):
        with open(img, 'rb') as f:
            requests.post(f"{base}/image", data={"token": TOKEN, "to": PHONE, "caption": msg}, files={"image": f}, timeout=20)

def get_sp500():
    try:
        import pandas as pd
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(requests.get(url, timeout=20).text)
        return tables[0]['Symbol'].str.replace('.','-', regex=False).tolist()
    except:
        return ["AAPL","MSFT","NVDA","TSLA","GOOGL","META","AMZN","NFLX","SPY","QQQ"]

HK_UNIVERSE = [
"0700.HK","0005.HK","0941.HK","1299.HK","1810.HK","09988.HK","1024.HK","3690.HK","2800.HK","0388.HK","2318.HK",
"0001.HK","0002.HK","0003.HK","0006.HK","0011.HK","0012.HK","0016.HK","0017.HK","0019.HK","0027.HK","0066.HK","0083.HK","0101.HK","0151.HK","0175.HK","0267.HK","0288.HK","0293.HK","0386.HK","0669.HK","0700.HK","0762.HK","0857.HK","0883.HK","0939.HK","0941.HK","0960.HK","0968.HK","0981.HK","09988.HK","1024.HK","1038.HK","1044.HK","1088.HK","1093.HK","1109.HK","1177.HK","1209.HK","1211.HK","1299.HK","1398.HK","1810.HK","1928.HK","1997.HK","2007.HK","2020.HK","2269.HK","2318.HK","2382.HK","2388.HK","2628.HK","2688.HK","3690.HK","3968.HK","3988.HK","9618.HK","9626.HK","9698.HK","9988.HK"
]

def get_cap(t):
    try:
        fi = yf.Ticker(t).fast_info
        cap = fi.market_cap or fi.get('market_cap')
        if cap: return cap
        return yf.Ticker(t).info.get('marketCap',0)
    except: return 0

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

now=datetime.now().strftime("%m/%d %H:%M")
US_LIST = get_sp500()
send(f"🔍 {now} 全市場掃描開始... 港股{len(HK_UNIVERSE)}隻 + 美股{len(US_LIST)}隻，將濾市值>200億港 / 100億美")

hits=0
for t in HK_UNIVERSE:
    cap = get_cap(t)
    if cap < HK_CAP: continue
    r=scan(t)
    if r:
        img,last=r; send(f"✅ HK {t} 市值{cap/1e8:.0f}億\n陽包陰+{last['Volume']/last['Vol_MA20']:.1f}x量+企55W\n現價 {last['Close']:.2f}", img); hits+=1; time.sleep(1)

for t in US_LIST:
    cap = get_cap(t)
    if cap < US_CAP: continue
    r=scan(t)
    if r:
        img,last=r; send(f"✅ US {t} 市值{cap/1e9:.1f}B\n陽包陰+{last['Volume']/last['Vol_MA20']:.1f}x量+企55W\n現價 {last['Close']:.2f}", img); hits+=1; time.sleep(1)

if hits==0: send(f"📭 {now} 全市場無符合")
else: send(f"🏁 完成，共 {hits} 隻符合")
