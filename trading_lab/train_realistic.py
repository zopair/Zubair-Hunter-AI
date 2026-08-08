"""Real-data walk-forward paper-training experiment.
Downloads public Binance spot klines and evaluates a tiny research policy with
realistic fees/spread/slippage. It is deliberately not a live-order system.
"""
import json, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from realistic_sim import FeeConfig, PaperBroker

BASE='https://api.binance.com/api/v3'
SYMBOLS=['BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT']
LIMIT=1000
START=5.0


def get(path):
    with urlopen(Request(BASE+path,headers={'User-Agent':'Zubair-Hunter-PaperLab/2.0'}),timeout=20) as r:
        return json.load(r)


def candles(symbol, interval='1m'):
    raw=get(f'/klines?symbol={symbol}&interval={interval}&limit={LIMIT}')
    return [{'t':x[0],'o':float(x[1]),'h':float(x[2]),'l':float(x[3]),'c':float(x[4]),'v':float(x[5])} for x in raw]


def feat(cs,i):
    c=cs[i]; p=cs[i-1]
    rng=max(c['h']-c['l'],1e-12); body=abs(c['c']-c['o'])
    uw=c['h']-max(c['o'],c['c']); lw=min(c['o'],c['c'])-c['l']
    hammer=lw>=2*max(body,1e-12) and uw<=.75*max(body,1e-12)
    bull=p['c']<p['o'] and c['c']>c['o'] and c['o']<=p['c'] and c['c']>=p['o']
    bear=p['c']>p['o'] and c['c']<c['o'] and c['o']>=p['c'] and c['c']<=p['o']
    mom=(c['c']-cs[i-5]['c'])/cs[i-5]['c']
    avg=sum(x['v'] for x in cs[i-20:i])/20
    return hammer,bull,bear,mom,c['v']/max(avg,1e-12)


def run(cs, start, end, fee):
    broker=PaperBroker(START,fee)
    trades=0; wins=0; gross_win=0.; gross_loss=0.; peak=START; max_dd=0.
    for i in range(start,end):
        hammer,bull,bear,mom,rv=feat(cs,i); p=cs[i]['c']
        # Research policy: only a small exposure; no forced trading.
        long=(hammer or bull) and mom>0 and rv>=1.0
        exit_=(bear or mom<0)
        if broker.position==0 and long:
            qty=(broker.cash*0.10)/p
            if broker.buy(qty,p,maker=False): trades += 1
        elif broker.position>0 and exit_:
            before=broker.realized
            if broker.sell(broker.position,p,maker=False):
                pnl=broker.realized-before
                wins += pnl>0
                if pnl>0: gross_win += pnl
                else: gross_loss += pnl
        eq=broker.mark_equity(p); peak=max(peak,eq); max_dd=max(max_dd,peak-eq)
    eq=broker.mark_equity(cs[end-1]['c'])
    return {'start':START,'equity':round(eq,6),'net_pnl':round(eq-START,6),
            'trades':trades,'win_rate':round(wins/max(1,trades),4),
            'profit_factor':round(gross_win/abs(gross_loss),4) if gross_loss else None,
            'max_drawdown':round(max_dd,6),'fees_paid':round(broker.fees_paid,6)}


def main():
    results=[]
    fee=FeeConfig(market='spot',maker_rate=.001,taker_rate=.001,bnb_discount=.25,use_bnb=False,spread_bps=1,slippage_bps=2)
    for symbol in SYMBOLS:
        cs=candles(symbol)
        n=len(cs); a=int(n*.60); b=int(n*.80)
        train=run(cs,20,a,fee); valid=run(cs,a,b,fee); test=run(cs,b,n,fee)
        results.append({'symbol':symbol,'interval':'1m','train':train,'validation':valid,'test':test})
        time.sleep(.2)
    payload={'asof':datetime.now(timezone.utc).isoformat(),'mode':'paper_only','results':results}
    with open('trading_lab/realistic_training_result.json','w') as f: json.dump(payload,f,indent=2)
    print(json.dumps(payload,indent=2))

if __name__=='__main__': main()
