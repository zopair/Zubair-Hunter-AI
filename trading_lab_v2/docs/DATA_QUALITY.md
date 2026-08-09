# Binance data quality safeguards

The training system must not assume public datasets are error-free.

Binance's public-data repository documents Klines, trades and aggTrades for
Spot and Futures and provides checksums for archived files. The repository's
issue tracker also contains examples of missing files and incidents where
trade-side fields were corrupted or suspiciously one-sided.

## Required checks

1. Verify archive checksum when available.
2. Normalize timestamps and reject impossible timestamps.
3. Reject non-positive price/quantity.
4. Check monotonicity of trade identifiers where applicable.
5. Detect suspiciously one-sided `is_buyer_maker` distributions.
6. Detect gaps in expected 1m bars.
7. Compare aggregate trade volume against kline volume within tolerance.
8. Mark affected intervals as `QUARANTINED` rather than filling them with
   synthetic values.
9. Record the exact data version/date used for every training run.
10. Never leak future rows into feature normalization or label construction.

## Historical order book limitation

Official Binance public archives do not provide a complete historical
best-bid/best-ask/order-book event archive equivalent to Klines/trades.
Therefore the simulator must distinguish between:

- `OBSERVED`: directly recorded order-book data;
- `RECONSTRUCTED`: inferred from trades/quotes;
- `STRESSED`: synthetic spread/depth assumptions.

Performance claims must report which mode was used.
