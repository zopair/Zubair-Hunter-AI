"""Cost-aware evaluation metrics for the training agent."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TradeResult:
    gross_pnl: float
    fees: float
    funding: float
    slippage: float
    mae: float
    mfe: float

    @property
    def net_pnl(self) -> float:
        return self.gross_pnl - self.fees - self.funding - self.slippage


def expectancy(results: list[TradeResult]) -> float:
    if not results:
        return 0.0
    return sum(r.net_pnl for r in results) / len(results)


def profit_factor(results: list[TradeResult]) -> float:
    gains = sum(max(r.net_pnl, 0.0) for r in results)
    losses = sum(max(-r.net_pnl, 0.0) for r in results)
    return gains / losses if losses else float("inf") if gains else 0.0


def max_drawdown(equity: list[float]) -> float:
    peak = float("-inf")
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        if peak:
            worst = max(worst, (peak - value) / peak)
    return worst


def score(results: list[TradeResult], equity: list[float]) -> dict:
    return {
        "expectancy": expectancy(results),
        "profit_factor": profit_factor(results),
        "max_drawdown_fraction": max_drawdown(equity),
        "trades": len(results),
        "net_pnl": sum(r.net_pnl for r in results),
    }
