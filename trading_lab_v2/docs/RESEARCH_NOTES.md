# Open-source research upgrades

## NautilusTrader

Use as the event-driven execution layer because it is designed to keep the
same core concepts across backtest, sandbox and live environments. Its Binance
integration and execution/matching abstractions are a better fit for our
microstructure simulator than a candle-only backtester.

## Binance Public Data

Use Binance's official public-data archive for reproducible historical data.
Prefer daily/monthly files and verify checksums. Klines, trades and aggTrades
are available for Spot and Futures. Do not assume all files are perfect: run
quality gates and quarantine suspicious intervals.

## VectorBT

Use for fast feature screening and parameter research only. Final evaluation
must pass through the event-driven simulator so fills, costs and latency are
represented.

## FinRL / RL

Use reinforcement learning only after the supervised edge model has learned
from clean, cost-adjusted labels. RL should optimize a reward that penalizes
fees, slippage, drawdown and excessive turnover, rather than raw return.

## Hummingbot / CCXT / python-binance

These projects are useful references for exchange connectivity, market-data
adapters and paper/live architecture. They should not replace the execution
simulator because a generic exchange abstraction can hide venue-specific
microstructure details.

## Key design conclusion

The platform should be hybrid:

`Binance historical data -> quality gates -> feature engine -> supervised edge model -> event-driven execution simulation -> walk-forward evaluation -> RL -> paper forward test`

No live order path is enabled by this training branch.
