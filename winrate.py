# winrate.py - 放喺你個stock scan repo
import yfinance as yf, pandas as pd
from datetime import timedelta

triggers = [
("2026-06-26","FMC"),("2026-07-23","WYNN"),("2026-07-28","GRAB"),
("2026-07-29","CHRW"),("2026-08-04","CE"),("2026-08-04","CTVA"),
("2026-08-04","WMB"),("2026-08-06","SPCX"),("2026-08-11","FHN"),
("2026-08-17","BIDU"),("2026-08-25","TME"),("2026-08-26","OKTA"),
("2026-08-31","ALGN"),("2026-09-08","FRT"),("2026-09-08","XEL"),
("2026-09-16","AXON"),("2026-09-18","0083.HK"),("2026-09-18","0288.HK"),
("2026-09-18","BKR"),("2026-09-18","DAL"),("2026-09-18","DRI"),
("2026-09-18","MAR"),("2026-09-18","MCO"),("2026-09-18","MMM"),
("2026-09-18","PH"),("2026-09-18","PRU"),("2026-09-18","TSN"),
("2026-09-21","1109.HK"),("2026-09-29","CMS"),("2026-09-29","DTE"),
("2026-09-29","EXC"),("2026-09-29","LNT"),("2026-09-29","PNW"),
("2026-09-29","SO"),("2026-10-01","BA"),("2026-10-01","NEE"),
("2026-10-02","EFX"),("2026-10-02","LW"),("2026-10-05","MDT"),
("2026-10-06","DHI"),("2026-10-15","IONQ"),("2026-10-15","NXPI"),
("2026-10-20","LCID"),("2026-10-20","UAL"),("2026-10-22","ALK"),
("2026-10-23","MOS"),
]

rows=[]
for d,t in triggers:
    df = yf.download(t, start=pd.to_datetime(d)-timedelta(days=7), end=pd.to_datetime(d)+timedelta(days=20), auto_adjust=True, progress=False)
    if len(df)<5: continue
    t_idx = df.index.get_indexer([pd.to_datetime(d)], method='bfill')[0]
    trigger_low = float(df.iloc[t_idx]['Low'])
    if t_idx+2 >= len(df): continue
    buy = float(df.iloc[t_idx+2]['Open'])
    fwd = df.iloc[t_idx+3:t_idx+13]
    hit = (fwd['Low'] < trigger_low).any()
    pnl = float(fwd.iloc[-1]['Close'] - buy)/buy*100
    rows.append([d,t,trigger_low,buy,hit,pnl])

res=pd.DataFrame(rows, columns=["date","ticker","stop_low","buy_T2_open","hit_stop","pnl_10d"])
res["win"] = (~res["hit_stop"]) & (res["pnl_10d"]>0)
print(res)
print(f"\n勝率: {res['win'].mean()*100:.1f}% | 止損率: {res['hit_stop'].mean()*100:.1f}% | 平均10日: {res['pnl_10d'].mean():.2f}%")
res.to_csv("winrate_result.csv", index=False)