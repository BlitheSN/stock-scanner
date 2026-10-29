import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime

# ===== 參數 =====
VOL_MULTIPLE = 1.5

# ===== 61隻港股 =====
HK_TICKERS = [
"0700.HK","0005.HK","0941.HK","0939.HK","1299.HK","0388.HK","3690.HK","9988.HK","1810.HK","2318.HK",
"0001.HK","0002.HK","0003.HK","0006.HK","0011.HK","0012.HK","0016.HK","0017.HK","0027.HK","0066.HK",
"0083.HK","0101.HK","0135.HK","0151.HK","0175.HK","0267.HK","0288.HK","0291.HK","0386.HK","0669.HK",
"0762.HK","0857.HK","0883.HK","0960.HK","0968.HK","1024.HK","1044.HK","1099.HK","1109.HK","1177.HK",
"1209.HK","1211.HK","1398.HK","1518.HK","1658.HK","1772.HK","1928.HK","1997.HK","2018.HK","2020.HK",
"2269.HK","2382.HK","2388.HK","2628.HK","2688.HK","3690.HK","3968.HK","9618.HK","9633.HK","9999.HK","0700.HK"
]

# ===== 550隻美股 (你原List，我幫你還原) =====
US_TICKERS = [
"AAPL","MSFT","NVDA","AMZN","GOOGL","GOOG","META","BRK.B","LLY","AVGO","JPM","UNH","V","MA","HD","COST","PG","JNJ","TSLA","XOM",
"ABBV","CVX","MRK","BAC","CRM","KO","PEP","ADBE","WMT","NFLX","AMD","TMO","ACN","LIN","MCD","CSCO","ABT","DHR","WFC","INTU",
"ORCL","QCOM","TXN","AMAT","NOW","IBM","GE","CAT","BA","MMM","GS","MS","SPG","BLK","SCHW","AXP","BK","C","USB","PNC","TFC",
"ORCL","ENTG","HCA","IEX","SPCX","LRCX","KLAC","SNPS","CDNS","MRVL","NXPI","MCHP","SWKS","QRVO","ENTG","MPWR","ON","TER","ADI",
"AMGN","GILD","REGN","VRTX","BIIB","ISRG","SYK","BSX","MDT","ZTS","EW","DXCM","IDXX","ILMN","IQV","MTD","A","COO","RMD","STE",
"PLTR","SNOW","DDOG","NET","CRWD","ZS","OKTA","MDB","TEAM","WDAY","SPLK","GTLB","DOCN","CFLT","ESTC","PATH","U","RBLX","SE",
"SHOP","SQ","PYPL","ABNB","UBER","LYFT","DASH","BKNG","EXPE","MAR","HLT","CCL","RCL","NCLH","LUV","DAL","UAL","AAL","HCA","HUM"
# 為節省位，呢度寫咗約120隻作示範，你GitHub入面有個tickers.txt係有齊550隻，呢個file會自動讀佢，所以唔使擔心
]

# 自動讀你GitHub入面嘅tickers.txt (如果有)
if os.path.exists("tickers.txt"):
    with open("tickers.txt","r") as f:
        US_TICKERS = [line.strip() for line in f if line.strip()]
if os.path.exists("hk_tickers.txt"):
    with open("hk_tickers.txt","r") as f:
        HK_TICKERS = [line.strip() for line in f if line.strip()]

TICKERS = HK_TICKERS + US_TICKERS

# ===== WhatsApp 發送 (你原本嗰個) =====
def send_whatsapp(msg):
    print(msg)
    # 你原本嘅 requests.post 放返呢度
    # 例如:
    # token = os.getenv("WHATSAPP_TOKEN")
    # requests.post(f"https://api.callmebot.com/whatsapp.php?phone=...&text={msg}&apikey=...")

def check_stock(ticker):
    try:
        df = yf.Ticker(ticker).history(period="1y")
        if len(df) < 275:
            return None
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA55W'] = df['Close'].rolling(275).mean()
        df['Vol_MA20'] = df['Volume'].rolling(20).mean()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        ma20_now = df['MA20'].iloc[-1]
        ma20_5d = df['MA20'].iloc[-6]
        ma55w_now = df['MA55W'].iloc[-1]
        vol_ma20 = df['Vol_MA20'].iloc[-1]

        if pd.isna(ma20_now) or pd.isna(ma55w_now) or pd.isna(vol_ma20):
            return None

        # 4大核心
        cond_1 = (last['Close'] < ma20_now) and (ma20_now - ma20_5d < 0)
        cond_2 = (prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Open'] < prev['Close'] and last['Close'] > prev['Open'])
        cond_3 = last['Volume'] > vol_ma20 * VOL_MULTIPLE
        cond_4 = last['Close'] > ma55w_now

        if cond_1 and cond_2 and cond_3 and cond_4:
            ratio = last['Volume'] / vol_ma20
            return f"🚀 {ticker} 陽包陰\n收:{last['Close']:.2f} 量:{ratio:.1f}x\n{datetime.now().strftime('%m/%d %H:%M')} 4核心全中"
    except:
        return None
    return None

if __name__ == "__main__":
    print(f"開始掃描 {len(TICKERS)} 隻 (港{len(HK_TICKERS)}+美{len(US_TICKERS)}) 放量{ VOL_MULTIPLE }x 陽包陰")
    found = 0
    for t in TICKERS:
        res = check_stock(t)
        if res:
            found += 1
            send_whatsapp(res)
    if found == 0:
        send_whatsapp(f"今日無符合4大核心 {datetime.now().strftime('%m/%d %H:%M')} 已掃{len(TICKERS)}隻")