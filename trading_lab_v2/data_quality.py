"""Data-quality gates for Binance public datasets.

Malformed, non-finite, or semantically invalid values are counted and rejected.
Rows that fail validation must be quarantined rather than silently trained on.
"""
from dataclasses import dataclass
import math


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


def _finite_number(value: object) -> float | None:
    """Return a finite numeric value; reject booleans and malformed inputs."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def validate_rows(rows: list[dict]) -> QualityReport:
    bad_timestamps = 0
    bad_prices = 0
    bad_quantities = 0

    for row in rows:
        timestamp = row.get("timestamp")
        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
            bad_timestamps += 1
        elif not math.isfinite(float(timestamp)):
            bad_timestamps += 1

        price = _finite_number(row.get("price"))
        if price is None or price <= 0:
            bad_prices += 1

        quantity = _finite_number(row.get("quantity"))
        if quantity is None or quantity <= 0:
            bad_quantities += 1

    sides = [row["is_buyer_maker"] for row in rows if "is_buyer_maker" in row]
    invalid_side_values = any(not isinstance(side, bool) for side in sides)
    suspicious_side_ratio = invalid_side_values
    if len(sides) >= 100 and not invalid_side_values:
        true_ratio = sum(sides) / len(sides)
        suspicious_side_ratio = true_ratio >= 0.999 or true_ratio <= 0.001

    return QualityReport(
        rows=len(rows),
        bad_timestamps=bad_timestamps,
        bad_prices=bad_prices,
        bad_quantities=bad_quantities,
        suspicious_side_ratio=suspicious_side_ratio,
    )
