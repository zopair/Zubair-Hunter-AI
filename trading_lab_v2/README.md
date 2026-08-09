# Binance Realistic Training Lab v2

A research-only, paper-trading environment for training and evaluating a Binance micro-scalping agent.

## Design

- Binance public historical data as the primary dataset source.
- Klines + aggTrades/trades for M1/M5 feature construction.
- Optional live public market-data adapter for forward paper testing.
- Event-driven execution simulation with explicit spread, slippage, latency, partial-fill and fee models.
- Futures-aware funding, leverage and maintenance-margin guards.
- Candlestick + price-action + imbalance/divergence features.
- Walk-forward train/validation/test splits with purging/embargo between splits.
- Cost-aware objective: maximize net expectancy, not raw accuracy or trade count.
- Stress tests for spread, slippage, latency and fee changes.
- No API keys and no live order submission.

## Important data-quality rule

Binance public data is checked before training. Known data-quality incidents (for example malformed trade-side fields) must be quarantined rather than silently used. See `docs/DATA_QUALITY.md`.

## Suggested stack

1. **NautilusTrader** for event-driven execution/matching simulation.
2. **Binance Public Data** for historical market data.
3. **VectorBT** for fast research and feature/parameter screening.
4. A lightweight supervised edge model before reinforcement learning.

The agent should only move to RL after the supervised model and execution simulator pass out-of-sample tests.
