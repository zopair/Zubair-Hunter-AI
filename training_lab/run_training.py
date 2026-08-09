"""Deterministic dry-run trainer: validates the pipeline without pretending to have live data."""
import json
from pathlib import Path
from .source_resolver import normalize

REQUIRED = ["klines", "trades"]

def run(dataset_dir="data"):
    p = Path(dataset_dir)
    files = {x.stem.lower(): x for x in p.glob("*")}
    missing = []
    for logical in REQUIRED:
        aliases = {
            "klines": {"kline", "klines", "candles", "ohlcv"},
            "trades": {"trade", "trades", "recent_trades"},
        }[logical]
        if not any(k in aliases for k in files):
            missing.append(logical)
    report = {
        "mode": "DRY_RUN_UNTIL_VALIDATED_DATA_EXISTS",
        "required_sources": REQUIRED,
        "missing": missing,
        "ready": not missing,
        "live_orders": False,
        "paper_capital_usd": 5.0,
        "max_trade_risk": 0.10,
    }
    Path("training_report.json").write_text(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
