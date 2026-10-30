import yfinance as yf, pandas as pd
from datetime import timedelta
import os

HISTORY_FILE = "triggers_history.csv"
STOP_FACTOR = 0.98

if not os.path.exists(HISTORY_FILE):
    print("No history file")
    exit()

hist = pd.read_csv(HISTORY_FILE)
rows=[]
for _, r in hist.iterrows():
    d = r["date"]; t = r["ticker"]
    try:
        df = yf.download(t, start=pd.to_datetime(d)-timedelta(days=7), end=pd.to_datetime(d)+timedelta(days=20), auto_adjust=True, progress=False, group_by='column')
        if df.empty or len(df)<5: continue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        t_idx = df.index.get_indexer([pd.to_datetime(d)], method='bfill')[0]
        if t_idx+2 >= len(df): continue
        trigger_low = float(df.iloc[t_idx]['Low']) * STOP_FACTOR
        buy = float(df.iloc[t_idx+2]['Open'])
        fwd = df.iloc[t_idx+3:t_idx+13]
        if fwd.empty: continue
        hit = bool((fwd['Low'] < trigger_low).any())
        pnl = float(fwd.iloc[-1]['Close'] - buy)/buy*100
        rows.append([d,t,trigger_low,buy,hit,pnl])
    except: continue

res=pd.DataFrame(rows, columns=["date","ticker","stop_98","buy_T2","hit_stop","pnl_10d"])
if not res.empty:
    res["win"] = (~res["hit_stop"]) & (res["pnl_10d"]>0)
    print(f"總火箭: {len(res)} | 勝率: {res['win'].mean()*100:.1f}% | 止損率: {res['hit_stop'].mean()*100:.1f}% | 平均: {res['pnl_10d'].mean():.2f}%")
    res.to_csv("winrate_result.csv", index=False)