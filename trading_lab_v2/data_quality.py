"""Data-quality gates for Binance public datasets.

Never silently train on malformed trade-side or timestamp data. Rows that fail
validation are quarantined and the affected interval is marked unreliable.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityReport:
    rows: int
    bad_timestamps: int
    bad_prices: int
    bad_quantities: int
    suspicious_side_ratio: bool

    @property
    def ok(self) -> bool:
        return (
            self.rows > 0
            and self.bad_timestamps == 0
            and self.bad_prices == 0
            and self.bad_quantities == 0
            and not self.suspicious_side_ratio
        )


def validate_rows(rows: list[dict]) -> QualityReport:
    bad_timestamps = sum(not isinstance(r.get("timestamp"), (int, float)) for r in rows)
    bad_prices = sum(float(r.get("price", 0)) <= 0 for r in rows)
    bad_quantities = sum(float(r.get("quantity", 0)) <= 0 for r in rows)

    sides = [r.get("is_buyer_maker") for r in rows if "is_buyer_maker" in r]
    suspicious_side_ratio = False
    if len(sides) >= 100:
        true_ratio = sum(bool(x) for x in sides) / len(sides)
        # A near-100% one-sided file is suspicious and requires inspection.
        suspicious_side_ratio = true_ratio >= 0.999 or true_ratio <= 0.001

    return QualityReport(
        rows=len(rows),
        bad_timestamps=bad_timestamps,
        bad_prices=bad_prices,
        bad_quantities=bad_quantities,
        suspicious_side_ratio=suspicious_side_ratio,
    )
