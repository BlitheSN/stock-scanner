import os
import yfinance as yf
import mplfinance as mpf
from datetime import datetime
import pandas as pd
import requests

INSTANCE_ID = os.getenv("ULTRA_INSTANCE")
TOKEN = os.getenv("ULTRA_TOKEN")
PHONE = "85252871318"
VOL_MULTIPLE = 1.5
HK_CAP = 20_000_000_000
US_CAP = 10_000_000_000

def send(msg, img=None):
    if not INSTANCE_ID or not TOKEN:
        print("Missing ULTRA env")
        return
    base = f"https://api.ultramsg.com/{INSTANCE_ID}"
    try:
        r = requests.post(f"{base}/messages/chat", data={"token": TOKEN, "to": PHONE, "body": msg}, timeout=20)
        print(f"Send text: {r.status_code}")
        if img and os.path.exists(img):
            with open(img, 'rb') as f:
                r2 = requests.post(f"{base}/messages/image", data={"token": TOKEN, "to": PHONE}, files={"image": f}, timeout=30)
                print(f"Send img: {r2.status_code}")
    except Exception as e:
        print(f"Send fail: {e}")

HK_UNIVERSE = ["0700.HK","0005.HK","0941.HK","1299.HK","0939.HK","1398.HK","2318.HK","0388.HK","0883.HK","1928.HK","9988.HK","3690.HK","9618.HK","1024.HK","1810.HK","2269.HK","2020.HK","9999.HK","2015.HK","0981.HK","0992.HK","0857.HK","0386.HK","0001.HK","0002.HK","0003.HK","0006.HK","0011.HK","0012.HK","0016.HK","0017.HK","0027.HK","0066.HK","0083.HK","0101.HK","0151.HK","0175.HK","0267.HK","0288.HK","0293.HK","0358.HK","0669.HK","0762.HK","0823.HK","0868.HK","0909.HK","0960.HK","0968.HK","1044.HK","1093.HK","1109.HK","1209.HK","1211.HK","1818.HK","1929.HK","1997.HK","2331.HK","2382.HK","2388.HK","2628.HK","2688.HK"]

def build_us_universe():
    tickers = ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","GOOG","BRK.B","LLY","AVGO","JPM","UNH","V","MA","HD","COST","XOM","PG","JNJ","ABBV","BAC","CRM","CVX","WMT","MRK","KO","ORCL","PEP","ACN","ADBE","AMD","LIN","TMO","MCD","CSCO","ABT","WFC","QCOM","DHR","TMUS","INTU","DIS","VZ","TXN","NKE","PM","IBM","MS","AMAT","CAT","GS","RTX","NOW","HON","ISRG","BKNG","LOW","EL","UNP","DE","AMGN","SYK","AXP","GE","LMT","MDT","BLK","ADI","CB","MMC","GILD","ADP","PLD","MDLZ","CI","SCHW","AMT","TGT","REGN","ETN","BDX","BSX","ZTS","C","SO","DUK","NEE","MO","SHW","PGR","APD","ITW","SLB","CL","ICE","AON","EW","HUM","PNC","APO","KKR","BX","PANW","SNPS","CDNS","KLAC","LRCX","MU","MRVL","MCHP","FTNT","CRWD","DDOG","ZS","NET","TEAM","WDAY","SNOW","MDB","PLTR","HOOD","COIN","MSTR","SPCX","ARM","RDDT","SMR","NVO","TSLA","TSM","ASML","BILI","NIO","LI","XPEV","BABA","PDD","JD","SE","MELI","NU","SHOP","SQ","AFRM","UPST","SOFI","DKNG","RBLX","IONQ","RGTI","QBTS","SMCI","APP","ANET","DELL","HPE","HPQ","INTC","GTLB","ESTC","OKTA","S","DOCU","SPOT","WBD","FOX","PARA","CMCSA","CHTR","T","LUMN","CIEN","JNPR","NTAP","WDC","STX","NXPI","ON","MPWR","ENTG","A","AAL","AAP","ABBV","ABNB","ABT","ACGL","ACN","ADBE","ADI","ADM","ADP","ADSK","AEE","AEP","AES","AFL","AIG","AIZ","AJG","AKAM","ALB","ALGN","ALLE","AMAT","AMCR","AMD","AME","AMGN","AMP","AMT","AMZN","ANET","ANSS","AON","AOS","APA","APD","APH","APTV","ARE","ATO","AVB","AVGO","AVY","AWK","AXON","AXP","AZO","BA","BALL","BAX","BBY","BDX","BEN","BF.B","BG","BIIB","BIO","BK","BKNG","BKR","BLDR","BLK","BMY","BR","BRO","BSX","BX","BXP","C","CAG","CAH","CARR","CAT","CB","CBOE","CBRE","CCI","CCL","CDAY","CDNS","CDW","CE","CEG","CF","CFG","CHD","CHRW","CHTR","CI","CINF","CL","CLX","CMA","CMCSA","CME","CMG","CMI","CMS","CNC","CNP","COF","COO","COP","COR","COST","CPB","CPRT","CPT","CRL","CRM","CSCO","CSGP","CSX","CTAS","CTLT","CTRA","CTSH","CTVA","CVS","CVX","CZR","D","DAL","DD","DE","DFS","DG","DGX","DHI","DHR","DIS","DLR","DLTR","DOV","DOW","DPZ","DRI","DTE","DUK","DVA","DVN","DXC","DXCM","EA","EBAY","ECL","ED","EFX","EG","EIX","EL","ELV","EMN","EMR","ENPH","EOG","EPAM","EQIX","EQR","EQT","ERIE","ES","ESS","ETN","ETR","ETSY","EVRG","EW","EXC","EXPD","EXPE","EXR","F","FANG","FAST","FCX","FDS","FDX","FE","FFIV","FI","FICO","FIS","FISV","FITB","FLT","FMC","FOX","FOXA","FRT","FSLR","FTNT","FTV","GD","GE","GEHC","GEN","GILD","GIS","GL","GLW","GM","GNRC","GOOG","GOOGL","GPC","GPN","GRMN","GS","GWW","HAL","HAS","HBAN","HBI","HCA","HD","HES","HIG","HII","HLT","HOLX","HON","HPE","HPQ","HRL","HSIC","HST","HSY","HUM","HWM","IBM","ICE","IDXX","IEX","IFF","INCY","INTC","INTU","INVH","IP","IPG","IQV","IR","IRM","ISRG","IT","ITW","IVZ","J","JBHT","JBL","JCI","JKHY","JNJ","JNPR","JPM","K","KDP","KEY","KEYS","KHC","KIM","KLAC","KMB","KMI","KMX","KO","KR","L","LDOS","LEN","LH","LHX","LIN","LKQ","LLY","LMT","LNT","LOW","LRCX","LUV","LVS","LW","LYB","LYV","MA","MAA","MAR","MAS","MCHP","MCK","MCO","MDLZ","MDT","MET","META","MGM","MHK","MKC","MKTX","MMC","MMM","MNST","MO","MOH","MOS","MPC","MPWR","MRK","MRNA","MRO","MS","MSCI","MSFT","MSI","MTB","MTCH","MTD","MU","NCLH","NDAQ","NDSN","NEE","NEM","NFLX","NKE","NI","NOC","NOW","NRG","NSC","NTAP","NTRS","NUE","NVDA","NVR","NWS","NWSA","NXPI","O","ODFL","OKE","OMC","ORCL","ORLY","OTIS","OXY","PANW","PARA","PAYC","PAYX","PCAR","PCG","PEAK","PEG","PEP","PFE","PFG","PG","PGR","PH","PHM","PKG","PLD","PM","PNC","PNR","PNW","POOL","PPG","PPL","PRU","PSA","PSX","PTC","PWR","PYPL","QCOM","QRVO","RCL","REG","REGN","RF","RJF","RL","RMD","ROK","ROL","ROP","ROST","RSG","RTX","SBAC","SBUX","SCHW","SEDG","SEE","SJM","SLB","SNA","SNPS","SO","SPG","SPGI","SRE","STE","STLD","STT","STX","STZ","SWK","SWKS","SYF","SYK","SYY","T","TAP","TDG","TDY","TECH","TEL","TER","TFC","TFX","TGT","TJX","TMO","TMUS","TPR","TR","TRGP","TRMB","TROW","TRV","TSCO","TSLA","TSN","TT","TTWO","TXN","TYL","UAL","UDR","UHS","ULTA","UNH","UNP","UPS","URI","USB","V","VFC","VLO","VMC","VRSK","VRSN","VRTX","VTR","VTRS","VZ","WAB","WAT","WBA","WBD","WDC","WEC","WELL","WFC","WM","WMB","WMT","WRB","WST","WTW","WY","WYNN","XEL","XOM","XYL","YUM","ZBH","ZBRA","ZION","ZTS","ASTS","RKLB","LUNR","SOUN"]
    tickers = list(dict.fromkeys(tickers))
    print(f"DEBUG 美股池已鎖死{len(tickers)}隻，含SPCX={'SPCX' in tickers}")
    return tickers

def check_stock(ticker):
    try:
        stk = yf.Ticker(ticker)
        hist = stk.history(period="1y", auto_adjust=True)
        if len(hist) < 60:
            return None
        try:
            info = stk.fast_info
            mcap = info.get('market_cap')
            if mcap:
                if ticker.endswith('.HK') and mcap < HK_CAP:
                    return None
                if not ticker.endswith('.HK') and mcap < US_CAP:
                    return None
        except:
            pass
        hist['MA20'] = hist['Close'].rolling(20).mean()
        hist['MA55W'] = hist['Close'].rolling(275).mean()
        hist['VolAvg20'] = hist['Volume'].rolling(20).mean()
        last = hist.iloc[-1]
        prev = hist.iloc[-2]
        ma_ref = last['MA55W'] if pd.notna(last['MA55W']) else last['MA20']
        prev_ma = prev['MA55W'] if pd.notna(prev['MA55W']) else prev['MA20']
        if pd.isna(ma_ref) or pd.isna(prev_ma):
            return None
        cond_vol = last['Volume'] > last['VolAvg20'] * VOL_MULTIPLE if pd.notna(last['VolAvg20']) else False
        cond_break = prev['Close'] < prev_ma and last['Close'] > ma_ref
        cond_above = last['Close'] > ma_ref
        if cond_vol and cond_break and cond_above:
            try:
                plot_data = hist.tail(120)
                fig_path = f"/tmp/{ticker.replace('.', '_')}.png"
                mpf.plot(plot_data, type='candle', mav=(20,55), volume=True, title=f"{ticker} 突破", style='yahoo', savefig=dict(fname=fig_path, dpi=100))
                return (ticker, fig_path, float(last['Close']), float(last['Volume']/last['VolAvg20']) if pd.notna(last['VolAvg20']) else 0)
            except:
                return (ticker, None, float(last['Close']), 0)
        return None
    except Exception as e:
        print(f"Check fail {ticker}: {e}")
        return None

def main():
    now = datetime.now().strftime("%m/%d %H:%M")
    hk_list = HK_UNIVERSE
    us_list = build_us_universe()
    send(f"🔍 {now} 真·全市場掃描開始... 港股{len(hk_list)}隻 + 美股{len(us_list)}隻，已濾>200億港 / 100億美")
    results = []
    for ticker in hk_list + us_list:
        res = check_stock(ticker)
        if res:
            results.append(res)
    if not results:
        send(f"📭 {now} 真·全市場無符合")
        return
    for ticker, img, price, vol_ratio in results:
        msg = f"🚀 {ticker} 突破\n收市: {price:.2f}\n放量: {vol_ratio:.1f}x\n{now}"
        send(msg, img)

if __name__ == "__main__":
    main()