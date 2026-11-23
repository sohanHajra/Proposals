"""Audit of one day and the gap rule (preregistration, Data, and the Deviation of 2026-11-23, item 4).

Total gap = every gap over 1 s between consecutive top of book rows on capture time, plus the stretch
from 00:00 to the first row and from the last row to 24:00 when either is over 1 s. A day is left out
if the total is over 3600 s. The decision is written into the audit file.
"""
from datetime import datetime, timezone

import numpy as np
import polars as pl

from .paths import RAW

GAP_US = 10**6
MAX_TOTAL_S = 3600


def day_bounds_us(day):
    d0 = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    a = int(d0.timestamp()) * 10**6
    return a, a + 86400 * 10**6


def ticker_frame(source, day, sym):
    cols = ["timestamp", "local_timestamp", "bid_price", "ask_price"]
    if source == "tardis":
        f = RAW / "tardis" / f"binance-futures_book_ticker_{day}_{sym}.csv.gz"
        return pl.read_csv(f, columns=cols, schema_overrides={"bid_price": pl.Float64, "ask_price": pl.Float64})
    if source == "cryptostruct":
        from .cryptostruct import out_file
    else:
        from .bybit import out_file
    return pl.read_parquet(out_file(day, sym, "ticker"), columns=cols)


def gap_rule(local_us, day):
    lo, hi = day_bounds_us(day)
    ts = np.sort(local_us[(local_us >= lo) & (local_us < hi)])
    if len(ts) == 0:
        return dict(rows_in_day=0, total_gap_s=86400.0, gaps_over_1s=0, left_out=True,
                    reason="no top of book rows in the day")
    d = np.diff(ts)
    big = d[d > GAP_US]
    head = ts[0] - lo; tail = hi - ts[-1]
    total = big.sum() + (head if head > GAP_US else 0) + (tail if tail > GAP_US else 0)
    out = dict(rows_in_day=int(len(ts)), gaps_over_1s=int(len(big)), longest_gap_s=float(big.max() / 1e6) if len(big) else 0.0,
               head_s=float(head / 1e6), tail_s=float(tail / 1e6), total_gap_s=float(total / 1e6),
               rule=f"left out if total gap over {MAX_TOTAL_S} s")
    out["left_out"] = bool(out["total_gap_s"] > MAX_TOTAL_S)
    out["reason"] = "total gap over one hour" if out["left_out"] else "kept"
    return out


def audit(source, day, sym, tick):
    b = ticker_frame(source, day, sym)
    out = dict(source=source, symbol=sym, day=day, top_of_book_rows=b.height)
    out["gap_rule"] = gap_rule(b["local_timestamp"].to_numpy(), day)
    sp = ((b["ask_price"] - b["bid_price"]) / tick).round(0)
    out["crossed_or_locked_rows"] = int((sp <= 0).sum())
    out["spread_1tick_share"] = float((sp == 1).mean())
    lat = (b["local_timestamp"] - b["timestamp"]) / 1000.0
    out["capture_minus_exchange_ms_quantiles"] = {str(q): float(lat.quantile(q)) for q in (0.01, 0.5, 0.99)}
    mid = (b["ask_price"] + b["bid_price"]) / 2
    out["mid_open_close"] = [float(mid[0]), float(mid[-1])]
    out["mid_median"] = float(mid.median())
    return out
