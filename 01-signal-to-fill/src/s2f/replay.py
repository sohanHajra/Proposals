"""Event driven replay of top of book updates and trades on exchange time.

Times are integer microseconds (Tardis exchange timestamps, whole ms in practice).
Order inside one timestamp: trades first, then book updates (preregistered).
My order is processed after every event stamped at or before t + d (primary tie rule),
or before events stamped exactly t + d when tie_after=False (robustness).
The order never changes the book.
"""
from dataclasses import dataclass
import numpy as np
import polars as pl

from .paths import RAW


@dataclass
class Book:
    ts: np.ndarray       # exchange time, microseconds
    bid_px: np.ndarray
    bid_qty: np.ndarray
    ask_px: np.ndarray
    ask_qty: np.ndarray


@dataclass
class Trades:
    ts: np.ndarray
    side: np.ndarray     # +1 buyer aggressor, -1 seller aggressor
    px: np.ndarray
    qty: np.ndarray


CLOCKS = {"exchange": "timestamp", "local": "local_timestamp"}


def load_day(day="2026-09-01", sym="BTCUSDT", clock="exchange"):
    """Load only the columns the replay needs. Prices stay float64 (float32 cannot hold 78549.6).
    clock="local" puts every row on its local capture time instead of exchange time (robustness 3)."""
    col = CLOCKS[clock]
    d = RAW / "tardis"
    b = pl.read_csv(d / f"binance-futures_book_ticker_{day}_{sym}.csv.gz",
                    columns=[col, "bid_price", "bid_amount", "ask_price", "ask_amount"],
                    schema_overrides={col: pl.Int64, "bid_price": pl.Float64, "ask_price": pl.Float64,
                                      "bid_amount": pl.Float32, "ask_amount": pl.Float32})
    t = pl.read_csv(d / f"binance-futures_trades_{day}_{sym}.csv.gz",
                    columns=[col, "side", "price", "amount"])
    # stable sorts keep the file order inside one timestamp
    b = b.sort(col, maintain_order=True)
    t = t.sort(col, maintain_order=True)
    book = Book(b[col].to_numpy(), b["bid_price"].to_numpy(), b["bid_amount"].to_numpy(),
                b["ask_price"].to_numpy(), b["ask_amount"].to_numpy())
    tr = Trades(t[col].to_numpy(), np.where(t["side"].to_numpy() == "buy", 1, -1),
                t["price"].to_numpy(), t["amount"].to_numpy())
    return book, tr


def merged_events(book: Book, tr: Trades):
    """Yield ('T', i) and ('B', j) in exchange time order, trades before book at equal time."""
    i = j = 0
    nt, nb = len(tr.ts), len(book.ts)
    while i < nt or j < nb:
        if j >= nb or (i < nt and tr.ts[i] <= book.ts[j]):
            yield "T", i
            i += 1
        else:
            yield "B", j
            j += 1


def book_index_at(book: Book, t, tie_after=True):
    """Index of the last book update my order sees when it arrives at time t.
    tie_after=True sees updates stamped exactly t; False sees only strictly earlier ones.
    Returns -1 when nothing has been seen yet."""
    side = "right" if tie_after else "left"
    return np.searchsorted(book.ts, t, side=side) - 1


def mid_at(book: Book, t, tie_after=True):
    k = book_index_at(book, t, tie_after)
    if k < 0:
        return np.nan
    return 0.5 * (book.bid_px[k] + book.ask_px[k])


def taker_fill(book: Book, t_decision, delay, side, qty, tie_after=True):
    """Marketable order sent at t_decision, arriving at t_decision + delay.
    Fills at the touch it sees. Top of book only, so qty above the touch is flagged
    (filled=touch quantity) rather than walked into deeper levels.
    Returns dict with px, filled, arrival index; px is nan if no book yet."""
    k = book_index_at(book, t_decision + delay, tie_after)
    if k < 0:
        return dict(px=np.nan, filled=0.0, k=k)
    if side > 0:
        px, avail = book.ask_px[k], book.ask_qty[k]
    else:
        px, avail = book.bid_px[k], book.bid_qty[k]
    return dict(px=float(px), filled=float(min(qty, avail)), k=int(k))
