"""Realistic paper-execution and cost model for Binance research.

No authentication and no real orders. Rates are configuration, not claims that
one user's account has those exact rates. Update the config from Binance's
current account/product fee schedule before using a different account tier.
"""
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class FeeConfig:
    market: Literal['spot','usd_m_futures'] = 'spot'
    maker_rate: float = 0.0010
    taker_rate: float = 0.0010
    bnb_discount: float = 0.25
    use_bnb: bool = False
    slippage_bps: float = 2.0
    spread_bps: float = 1.0
    funding_rate: float = 0.0
    funding_period_hours: float = 8.0
    maintenance_margin_rate: float = 0.005
    leverage: float = 1.0

@dataclass
class Fill:
    side: str
    qty: float
    price: float
    notional: float
    fee: float
    slippage_cost: float

class PaperBroker:
    def __init__(self, equity: float, fees: FeeConfig):
        self.cash = float(equity)
        self.position = 0.0
        self.entry = 0.0
        self.realized = 0.0
        self.fees_paid = 0.0
        self.fees = fees

    def _rate(self, maker: bool) -> float:
        r = self.fees.maker_rate if maker else self.fees.taker_rate
        return r * (1.0 - self.fees.bnb_discount) if self.fees.use_bnb else r

    def execute(self, side: str, qty: float, mid: float, maker: bool=False) -> Fill:
        direction = 1 if side.lower() == 'buy' else -1
        slip = self.fees.slippage_bps / 10000.0
        half_spread = self.fees.spread_bps / 20000.0
        exec_price = mid * (1.0 + direction * (slip + half_spread))
        notional = abs(qty * exec_price)
        fee = notional * self._rate(maker)
        self.fees_paid += fee
        return Fill(side, qty, exec_price, notional, fee, abs(exec_price-mid)*abs(qty))

    def mark_equity(self, price: float) -> float:
        return self.cash + self.position * price

    def buy(self, qty: float, mid: float, maker=False):
        f = self.execute('buy', qty, mid, maker)
        cost = f.notional + f.fee
        if cost > self.cash: return None
        old = self.position
        self.cash -= cost
        self.position += qty
        self.entry = ((self.entry*old)+(f.price*qty))/self.position if self.position else 0.0
        return f

    def sell(self, qty: float, mid: float, maker=False):
        qty = min(qty, self.position)
        if qty <= 0: return None
        f = self.execute('sell', qty, mid, maker)
        self.cash += f.notional - f.fee
        self.realized += (f.price-self.entry)*qty - f.fee
        self.position -= qty
        if self.position <= 1e-12: self.position=0.0; self.entry=0.0
        return f

    def funding(self, hours: float, mark_price: float):
        if self.fees.market != 'usd_m_futures' or self.position == 0: return 0.0
        payment = self.position * mark_price * self.fees.funding_rate * (hours/self.fees.funding_period_hours)
        self.cash -= payment
        self.realized -= payment
        return payment

    def liquidation_price_estimate(self):
        if self.position == 0 or self.fees.market != 'usd_m_futures': return None
        # Conservative research guard, not Binance's exact liquidation engine.
        return self.entry * (1.0 - (1.0/self.fees.leverage) + self.fees.maintenance_margin_rate)

    def summary(self, price: float):
        return {'cash': self.cash, 'position': self.position,
                'equity': self.mark_equity(price), 'realized_pnl': self.realized,
                'fees_paid': self.fees_paid,
                'liquidation_guard': self.liquidation_price_estimate()}
