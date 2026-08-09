"""Small real-data Binance experiment for CI.

Downloads public 1m candles (no credentials), applies a deterministic
micro-scalping baseline, charges configurable costs, and writes metrics.
This is a validation experiment, not a claim of predictive profitability.
"""
import json, time, urllib.parse, urllib.request
from pathlib import Path

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "1m"
LIMIT = 500
FEE_RATE = 0.0004
SLIPPAGE_BPS = 2.0
START_CASH = 5.0
RISK = 0.10


def get_klines(symbol):
    q = urllib.parse.urlencode({"symbol": symbol, "interval": INTERVAL, "limit": LIMIT})
    url = "https://api.binance.com/api/v3/klines?" + q
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())


def run(symbol):
    rows = get_klines(symbol)
    cash = START_CASH; peak = cash; trades = 0; wins = 0
    pos = None; net_fees = 0.0
    for i in range(2, len(rows)):
        prev = float(rows[i-1][4]); close = float(rows[i][4])
        ret = (prev / float(rows[i-2][4])) - 1
        # Simple research baseline: follow a short-term impulse only when
        # the estimated move exceeds round-trip cost by a margin.
        cost = 2 * (FEE_RATE + SLIPPAGE_BPS / 10000)
        if pos is None and ret > cost * 1.5:
            qty_cash = cash * RISK
            if qty_cash > 0:
                entry = close * (1 + SLIPPAGE_BPS / 10000)
                fee = qty_cash * FEE_RATE
                pos = (entry, qty_cash, fee)
                net_fees += fee
                trades += 1
        elif pos is not None and ret < 0:
            entry, qty_cash, entry_fee = pos
            exitp = close * (1 - SLIPPAGE_BPS / 10000)
            gross = qty_cash * ((exitp / entry) - 1)
            fee = qty_cash * FEE_RATE
            pnl = gross - fee
            cash += pnl
            net_fees += fee
            if pnl > 0: wins += 1
            pos = None
            peak = max(peak, cash)
    if pos:
        entry, qty_cash, entry_fee = pos
        exitp = float(rows[-1][4]) * (1 - SLIPPAGE_BPS / 10000)
        cash += qty_cash * ((exitp / entry) - 1) - qty_cash * FEE_RATE
        net_fees += qty_cash * FEE_RATE
    return {"symbol": symbol, "start_cash": START_CASH, "end_cash": round(cash, 8),
            "net_pnl": round(cash-START_CASH, 8), "trades": trades,
            "wins": wins, "win_rate": round(wins/trades, 4) if trades else 0,
            "fees": round(net_fees, 8), "data_rows": len(rows),
            "risk_per_trade": RISK, "live_orders": False}


def main():
    out = {"mode": "REAL_BINANCE_PUBLIC_DATA_PAPER_EXPERIMENT", "results": []}
    for s in SYMBOLS:
        try: out["results"].append(run(s))
        except Exception as e: out["results"].append({"symbol": s, "error": str(e)})
        time.sleep(0.2)
    Path("training_report.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))

if __name__ == "__main__": main()
