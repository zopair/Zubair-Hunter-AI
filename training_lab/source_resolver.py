"""Resolve Binance dataset/product naming variations without hard-coding one layout.

Accepts aliases such as spot/futures, usdm/usdt-m, coinm/coin-m and kline/klines.
The resolver never silently substitutes a different market: ambiguity is an error.
"""
ALIASES = {
    "spot": {"spot", "spot_market"},
    "usdm": {"usdm", "usd-m", "usdt-m", "usdtm", "futures", "futures_usdm"},
    "coinm": {"coinm", "coin-m", "coin_m", "coin_futures"},
    "klines": {"kline", "klines", "candles", "candlestick", "ohlcv"},
    "aggtrades": {"aggtrade", "aggtrades", "aggregate_trades", "aggregated_trades"},
    "trades": {"trade", "trades", "recent_trades"},
    "book": {"book", "orderbook", "order_book", "depth"},
}

def normalize(value: str) -> str:
    x = value.strip().lower().replace(" ", "_")
    for canonical, names in ALIASES.items():
        if x in names:
            return canonical
    raise ValueError(f"Unknown/ambiguous Binance source name: {value!r}")


def resolve_many(values):
    result = [normalize(v) for v in values]
    if len(set(result)) != len(result):
        raise ValueError("Duplicate logical sources after normalization")
    return result
