"""Download real Binance public klines and run a fee-aware paper backtest.
No API keys are required. This is research/paper trading only.
"""
import csv, json, math, time
from datetime import datetime, timezone
from urllib.request import urlopen, Request

BASE='https://api.binance.com/api/v3'
SYMBOLS=['BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT']
INTERVAL='1m'
LIMIT=1000
START_CAPITAL=100.0
FEE_RATE=0.001

def get(path):
    req=Request(BASE+path,headers={'User-Agent':'Binance-Paper-Lab/1.0'})
    with urlopen(req,timeout=20) as r:return json.load(r)

def candles(symbol):
    raw=get(f'/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}')
    return [{'t':x[0],'o':float(x[1]),'h':float(x[2]),'l':float(x[3]),'c':float(x[4]),'v':float(x[5])} for x in raw]

def features(cs,i):
    c=cs[i]; p=cs[i-1] if i else c
    rng=max(c['h']-c['l'],1e-12); body=abs(c['c']-c['o']); uw=c['h']-max(c['o'],c['c']); lw=min(c['o'],c['c'])-c['l']
    doji=body/rng<.10; hammer=lw>2*max(body,1e-12) and uw<.75*max(body,1e-12)
    bull=p['c']<p['o'] and c['c']>c['o'] and c['o']<=p['c'] and c['c']>=p['o']
    bear=p['c']>p['o'] and c['c']<c['o'] and c['o']>=p['c'] and c['c']<=p['o']
    mom=(c['c']-cs[max(0,i-5)]['c'])/max(cs[max(0,i-5)]['c'],1e-12)
    avg=sum(x['v'] for x in cs[max(0,i-20):i+1])/max(1,len(cs[max(0,i-20):i+1]))
    return dict(doji=doji,hammer=hammer,bull=bull,bear=bear,mom=mom,relvol=c['v']/max(avg,1e-12))

def backtest(cs):
    cash=START_CAPITAL; qty=0.; entry=0.; trades=[]
    for i in range(20,len(cs)):
        f=features(cs,i); p=cs[i]['c']
        long_signal=(f['bull'] or f['hammer']) and f['mom']>0 and f['relvol']>=1
        exit_signal=f['bear'] or (f['mom']<0)
        if qty==0 and long_signal:
            notional=cash*0.10; fee=notional*FEE_RATE; qty=notional/p; cash-=notional+fee; entry=p
        elif qty>0 and exit_signal:
            notional=qty*p; fee=notional*FEE_RATE; cash+=notional-fee; pnl=(p-entry)*qty-fee; trades.append(pnl); qty=0; entry=0
    equity=cash+qty*cs[-1]['c']; wins=sum(x>0 for x in trades); loss=sum(x for x in trades if x<0)
    return {'start':START_CAPITAL,'equity':equity,'net_pnl':equity-START_CAPITAL,'trades':len(trades),'win_rate':wins/max(1,len(trades)),'profit_factor':sum(x for x in trades if x>0)/abs(loss) if loss else None}

def main():
    out=[]
    for s in SYMBOLS:
        cs=candles(s); r=backtest(cs); r['symbol']=s;r['interval']=INTERVAL;r['asof']=datetime.now(timezone.utc).isoformat();out.append(r);time.sleep(.2)
    print(json.dumps(out,indent=2))
    with open('trading_lab/latest_backtest.json','w') as f:json.dump(out,f,indent=2)
if __name__=='__main__':main()
