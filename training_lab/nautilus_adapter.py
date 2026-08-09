"""Minimal event-driven adapter contract for a future NautilusTrader backend.

Keeps the research environment independent from the live broker connector.
All fills are paper fills and pass through the cost model.
"""
from dataclasses import dataclass

@dataclass
class Fill:
    symbol: str
    side: str
    qty: float
    price: float
    fee: float
    slippage: float
    funding: float = 0.0

class ExecutionAdapter:
    def __init__(self, fee_rate=0.0004, slippage_bps=2.0, latency_ms=50):
        self.fee_rate = fee_rate
        self.slippage_bps = slippage_bps
        self.latency_ms = latency_ms

    def paper_fill(self, symbol, side, qty, mid_price):
        slip = mid_price * self.slippage_bps / 10_000
        price = mid_price + slip if side.lower() == "buy" else mid_price - slip
        fee = abs(price * qty) * self.fee_rate
        return Fill(symbol, side, qty, price, fee, slip)
