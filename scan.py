import yfinance as yf, mplfinance as mpf, requests, os, time
from datetime import datetime
import pandas as pd

INSTANCE_ID = os.getenv("ULTRA_INSTANCE")
TOKEN = os.getenv("ULTRA_TOKEN")
PHONE = "85252871318"
VOL_MULTIPLE = 1.8
HK_CAP = 20_000_000_000
US_CAP = 10_000_000_000

def send(msg, img=None):
    base = f"https://api.ultramsg.com/{INSTANCE_ID}/messages"
    try:
        requests.post(f"{base}/chat", data={"token": TOKEN, "to": PHONE, "body": msg}, timeout=20)
        if img and os.path.exists(img):
            with open(img, 'rb') as f:
                requests.post(f"{base}/image", data={"token": TOKEN, "to": PHONE, "caption": msg}, files={"image": f}, timeout=20)
    except Exception as e:
        print(f"Send fail: {e}")

HK_UNIVERSE = ["0700.HK","0005.HK","0941.HK","1299.HK","1810.HK","09988.HK","1024.HK","3690.HK","2800.HK","0388.HK","2318.HK","0001.HK","0002.HK","0003.HK","0006.HK","0011.HK","0012.HK","0016.HK","0017.HK","0019.HK","0027.HK","0066.HK","0083.HK","0101.HK","0151.HK","0175.HK","0267.HK","0288.HK","0293.HK","0386.HK","0669.HK","0762.HK","0857.HK","0883.HK","0939.HK","0960.HK","0968.HK","0981.HK","1038.HK","1044.HK","1088.HK","1093.HK","1109.HK","1177.HK","1209.HK","1211.HK","1398.HK","1928.HK","1997.HK","2007.HK","2020.HK","2269.HK","2382.HK","2388.HK","2628.HK","2688.HK","3968.HK","3988.HK","9618.HK","9626.HK","9698.HK"]

# 原本你寫死嗰500隻，我幫你加埋自動抓
def build_us_universe():
    base = ["AAPL","MSFT","NVDA","AMZN","GOOGL","GOOG","META","BRK-B","AVGO","LLY","JPM","UNH","V","MA","COST","HD","PG","NFLX","ABBV","CVX","KO","WMT","CRM","XOM","BAC","MRK","PEP","ORCL","CSCO","ACN","LIN","TMO","MCD","ABT","WFC","ADBE","TMUS","DHR","GE","IBM","DIS","VZ","CAT","QCOM","GS","PFE","INTU","AMAT","BKNG","TXN","NOW","ISRG","SPGI","AMGN","UBER","NEE","LOW","MS","BLK","HON","EL","SYK","DE","AXP","GILD","TJX","ADP","AMT","SCHW","MDT","C","BSX","VRTX","REGN","LRCX","ADI","MMC","CB","PGR","CI","ETN","KLAC","MDLZ","ZTS","FI","SO","SHW","BDX","ICE","PANW","MU","HCA","APD","CMCSA","EOG","ITW","WM","MCO","AON","DUK","SLB","MAR","FCX","NKE","MO","USB","TGT","MCK","PH","ADSK","PYPL","SNPS","CDNS","ABNB","COP","WELL","D","NOC","GD","FDX","ECL","MSI","AIG","KMI","NEM","PSA","TRV","CTAS","AFL","SPG","O","ROST","HUM","PRU","IT","LULU","AZO","ODFL","FAST","VRSK","IDXX","TDG","ANSS","CTSH","CPRT","EA","MNST","PCAR","EXC","PAYX","VLO","EXR","DLR","SBUX","WMB","CTVA","WEC","PPG","CBOE","RMD","KHC","DHI","YUM","WAB","KEYS","CDW","TT","MLM","MTD","SBAC","GWW","AMP","EIX","HLT","AVB","AWK","FTNT","PWR","TSCO","CHTR","TTWO","EQR","IFF","XYL","ULTA","VTR","FE","BXP","ARE","CBRE","NDSN","WY","HOLX","LHX","STLD","BLL","IEX","WRB","MTCH","BR","ETSY","CNP","DOV","NVR","EXPD","LDOS","VMC","PFG","PEAK","ETR","J","JBHT","MAA","LVS","RCL","AEE","HUBB","HPE","VTRS","NWSA","COO","CMA","ALK","AIZ","APA","BBY","BIO","CHRW","DVA","DVN","FMC","GLW","HAS","IPG","IVZ","JBLU","LEG","LNC","MGM","MOS","NRG","NWL","OGN","PENN","RL","TAP","UAA","WHR","WRK","ZION"]
    try:
        sp = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].str.replace('.', '-', regex=False).tolist()
    except: sp = []
    try:
        nq = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[4]['Ticker'].tolist()
    except: nq = []
    # 手動確保SPCX一定在
    manual = ['SPCX','ARM','RDDT']
    all_t = list(set(base + sp + nq + manual))
    # 去重 + 清理
    all_t = [t.strip().upper() for t in all_t if t]
    print(f"US池：base {len(base)} + S&P {len(sp)} + Nasdaq100 {len(nq)} + manual {len(manual)} = {len(all_t)}")
    return all_t

US_UNIVERSE = build_us_universe()

def get_cap(t):
    try:
        fi = yf.Ticker(t).fast_info
        cap = fi.market_cap
        if cap: return cap
    except: pass
    try: return yf.Ticker(t).info.get('marketCap',0)
    except: return 0

def scan(t):
    try:
        df = yf.Ticker(t).history(period="2y", auto_adjust=True)
        if len(df)<60: return None
        df['MA20']=df['Close'].rolling(20).mean()
        df['MA20_slope']=df['MA20'].diff(5)
        df['Vol_MA20']=df['Volume'].rolling(20).mean()
        
        # 周線
        weekly=df['Close'].resample('W').last()
        has_55w = len(weekly)>=55
        if has_55w:
            wma55 = weekly.rolling(55).mean().iloc[-1]
            df['WMA55']=weekly.rolling(55).mean().reindex(df.index, method='ffill')
            last_wma = df['WMA55'].iloc[-1]
            above_trend = df['Close'].iloc[-1] > last_wma
            trend_label = "企55W"
        else:
            # 新股fallback：用20日線
            last_wma = df['MA20'].iloc[-1]
            above_trend = df['Close'].iloc[-1] > last_wma
            trend_label = f"新股用MA20(周{len(weekly)})"

        last, prev = df.iloc[-1], df.iloc[-2]
        if pd.isna(last['MA20']) or pd.isna(last['Vol_MA20']): return None

        ok = (last['Close']<last['MA20'] and last['MA20_slope']<0 and prev['Close']<prev['Open'] and last['Close']>last['Open'] and last['Open']<prev['Close'] and last['Close']>prev['Open'] and last['Volume']>last['Vol_MA20']*VOL_MULTIPLE and above_trend)
        if ok:
            img=f"/tmp/{t.replace('.','_')}.png"
            mpf.plot(df.tail(90), type='candle', mav=20, volume=True, title=f"{t} {last['Close']:.2f} {trend_label}", style='yahoo', savefig=dict(fname=img, dpi=110))
            return img, last, trend_label
    except Exception as e:
        # print(f"{t} err {e}")
        return None

now=datetime.now().strftime("%m/%d %H:%M")
send(f"🔍 {now} 真·全市場掃描開始... 港股{len(HK_UNIVERSE)}隻 + 美股{len(US_UNIVERSE)}隻，已濾>200億港 / 100億美")

hits=0
for t in HK_UNIVERSE:
    if get_cap(t) < HK_CAP: continue
    r=scan(t)
    if r:
        img,last,label=r; send(f"✅ HK {t} {last['Volume']/last['Vol_MA20']:.1f}x量 {label}\n現價 {last['Close']:.2f}", img); hits+=1; time.sleep(0.8)

for t in US_UNIVERSE:
    if get_cap(t) < US_CAP: continue
    r=scan(t)
    if r:
        img,last,label=r; send(f"✅ US {t} {last['Volume']/last['Vol_MA20']:.1f}x量 {label}\n現價 {last['Close']:.2f}", img); hits+=1; time.sleep(0.8)

if hits==0: send(f"📭 {now} 真·全市場無符合")
else: send(f"🏁 完成，共 {hits} 隻符合")