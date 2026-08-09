"""Binance public-data downloader/validator skeleton.

Downloads are intentionally explicit: no API keys and no live trading.
The trainer consumes only validated historical files.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv, hashlib, urllib.request

@dataclass
class DatasetReport:
    rows: int
    first_ts: int | None
    last_ts: int | None
    duplicates: int
    invalid: int
    gaps: int
    sha256: str


def download(url: str, out: Path) -> str:
    out.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, out)
    h = hashlib.sha256()
    with out.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate_klines(path: Path, expected_ms=60_000) -> DatasetReport:
    rows = 0; first = last = None; dup = invalid = gaps = 0; prev = None
    with path.open(newline='') as f:
        reader = csv.reader(f)
        for r in reader:
            if not r: continue
            try:
                ts = int(r[0]); o,h,l,c = map(float, r[1:5]); v = float(r[5])
                if h < max(o,c,l) or l > min(o,c,h) or v < 0: invalid += 1
            except (ValueError, IndexError):
                invalid += 1; continue
            rows += 1
            if first is None: first = ts
            if prev is not None:
                if ts == prev: dup += 1
                elif ts - prev != expected_ms: gaps += 1
            prev = ts; last = ts
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return DatasetReport(rows, first, last, dup, invalid, gaps, h)

if __name__ == '__main__':
    print('Use download(url, path) then validate_klines(path).')
