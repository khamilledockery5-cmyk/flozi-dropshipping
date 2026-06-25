"""Market data sources.

Two ways to get OHLC bars, neither of which needs the network:

* ``load_csv``       — read a CSV with columns: timestamp,open,high,low,close[,volume]
* ``synthetic_ohlc`` — generate realistic random-walk bars for offline demos
                       and tests (geometric Brownian motion with intrabar range).

A ``Bar`` is a simple immutable record. Series are plain lists of ``Bar``.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Bar:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


def closes(bars: List[Bar]) -> List[float]:
    return [b.close for b in bars]


def load_csv(path: str) -> List[Bar]:
    bars: List[Bar] = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        required = {"open", "high", "low", "close"}
        if not required.issubset({c.lower() for c in (reader.fieldnames or [])}):
            raise ValueError(f"CSV must contain columns: {sorted(required)}")
        for row in reader:
            row = {k.lower(): v for k, v in row.items()}
            bars.append(
                Bar(
                    timestamp=row.get("timestamp", row.get("date", "")),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume", 0) or 0),
                )
            )
    if not bars:
        raise ValueError("CSV contained no rows")
    return bars


def synthetic_ohlc(
    n: int = 500,
    start_price: float = 100.0,
    drift: float = 0.0003,
    volatility: float = 0.02,
    seed: Optional[int] = 42,
) -> List[Bar]:
    """Generate `n` daily-ish bars via geometric Brownian motion.

    `drift` is the per-bar mean log return; `volatility` the per-bar stdev.
    The default has a slight positive drift so trend logic has something to
    work with, but trades still lose plenty of the time.
    """
    rng = random.Random(seed)
    bars: List[Bar] = []
    price = start_price
    for i in range(n):
        ret = drift + volatility * rng.gauss(0.0, 1.0)
        new_close = max(0.01, price * math.exp(ret))
        o = price
        c = new_close
        # intrabar wick: random extension beyond the open/close body
        body_hi = max(o, c)
        body_lo = min(o, c)
        wick = volatility * price * abs(rng.gauss(0.0, 1.0))
        high = body_hi + wick * rng.random()
        low = max(0.01, body_lo - wick * rng.random())
        bars.append(
            Bar(
                timestamp=f"T{i:05d}",
                open=round(o, 4),
                high=round(high, 4),
                low=round(low, 4),
                close=round(c, 4),
                volume=round(rng.uniform(1_000, 10_000), 2),
            )
        )
        price = new_close
    return bars
