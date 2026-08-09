# Real Binance Training Dataset Contract

Each event must carry `source_quality`: `OBSERVED`, `RECONSTRUCTED`, or `STRESSED`.

Required event families:
- 1m/5m OHLCV
- trades / aggTrades
- funding and open interest when available
- order-book snapshots/deltas when genuinely observed
- execution costs: spread, slippage, latency, fee tier

The trainer must reject future leakage, duplicate timestamps, invalid prices/quantities,
large unexplained gaps, and corrupted archive segments.

Walk-forward protocol:
- chronological train/validation/test
- purge and embargo around split boundaries
- no random shuffling across time

Evaluation must report net P&L after costs, expectancy, profit factor, max drawdown,
turnover, trade count, and out-of-sample performance. Accuracy alone is not a success metric.
