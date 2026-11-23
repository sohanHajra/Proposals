"""One day from any 01.b source in the shapes the 01 code uses: (book, trades, S) as s2f.passive.prep_day
returns them. The steps are the ones in s2f.replay.load_day and s2f.passive.prep_day at tag
v0.1-signal-to-fill: rows stably sorted by exchange time, top of book sizes held as float32, prices
as float64, and S built from the rows where my side of the top of book changed. On Tardis
BTCUSDT 2026-09-01 this gives exactly what prep_day gives (tests/test_load.py).

Sources
  tardis        the Tardis csv files, any symbol
  cryptostruct  the parquet files written by s2fb.cryptostruct
  bybit         the parquet files written by s2fb.bybit
"""
import gc

import numpy as np
import polars as pl

from .paths import RAW
from .guard import check_day_allowed

import s2f.paths  # noqa: F401  (01 code, put on the path by s2fb.paths)
from s2f.paths import float_prices
from s2f.replay import Book, Trades

BOOK_COLS = ["timestamp", "bid_price", "bid_amount", "ask_price", "ask_amount"]
TRADE_COLS = ["timestamp", "side", "price", "amount"]


def frames(source, day, sym):
    """Top of book, trades and five level frames, each with exchange timestamps in microseconds."""
    if source == "tardis":
        d = RAW / "tardis"
        fb = d / f"binance-futures_book_ticker_{day}_{sym}.csv.gz"
        ft = d / f"binance-futures_trades_{day}_{sym}.csv.gz"
        fs = d / f"binance-futures_book_snapshot_5_{day}_{sym}.csv.gz"
        b = pl.read_csv(fb, columns=BOOK_COLS,
                        schema_overrides={"timestamp": pl.Int64, "bid_price": pl.Float64, "ask_price": pl.Float64,
                                          "bid_amount": pl.Float32, "ask_amount": pl.Float32})
        t = pl.read_csv(ft, columns=TRADE_COLS, schema_overrides=float_prices(ft))
        s = pl.read_csv(fs, schema_overrides=float_prices(fs))
        return b, t, s
    if source == "cryptostruct":
        from .cryptostruct import out_file
    elif source == "bybit":
        from .bybit import out_file
    else:
        raise ValueError(source)
    b = pl.read_parquet(out_file(day, sym, "ticker"), columns=BOOK_COLS).with_columns(
        pl.col("bid_amount").cast(pl.Float32), pl.col("ask_amount").cast(pl.Float32))
    t = pl.read_parquet(out_file(day, sym, "trades"), columns=TRADE_COLS)
    s = pl.read_parquet(out_file(day, sym, "snap5"))
    return b, t, s


def _sorted_columns(path, cols, f32=()):
    """Columns of a parquet file as numpy arrays, stably sorted by timestamp. Read one column at a time
    so a busy day fits in memory. Same result as a polars stable sort on timestamp."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    f = pq.ParquetFile(str(path))
    ts = f.read(columns=["timestamp"]).column(0).to_numpy()
    o = None if (np.diff(ts) >= 0).all() else np.argsort(ts, kind="stable")
    out = {"timestamp": np.array(ts, copy=True) if o is None else ts[o]}
    del ts
    for c in cols:
        if c == "timestamp":
            continue
        a = f.read(columns=[c]).column(0)
        if c == "side":
            import pyarrow.compute as pc
            a = pc.equal(a, "buy").to_numpy(zero_copy_only=False)      # True for a buyer taker
        else:
            a = a.to_numpy()
        if c in f32:
            a = a.astype(np.float32)
        out[c] = np.array(a, copy=True) if o is None else a[o]
        del a
        pa.default_memory_pool().release_unused()
    return out


def prep(source, day, sym="BTCUSDT"):
    check_day_allowed(day, sym, source)
    if source == "tardis":
        return _prep_frames(*frames(source, day, sym))
    mod = __import__(f"s2fb.{source}", fromlist=["out_file"])
    b = _sorted_columns(mod.out_file(day, sym, "ticker"), BOOK_COLS, f32=("bid_amount", "ask_amount"))
    book = Book(b["timestamp"], b["bid_price"], b["bid_amount"], b["ask_price"], b["ask_amount"])
    del b
    t = _sorted_columns(mod.out_file(day, sym, "trades"), TRADE_COLS)
    tr = Trades(t["timestamp"], np.where(t["side"], 1, -1), t["price"], t["amount"])
    del t
    snap = pl.read_parquet(mod.out_file(day, sym, "snap5"))
    return _finish(book, tr, snap)


def _prep_frames(b, t, snap):
    b = b.sort("timestamp", maintain_order=True)
    t = t.sort("timestamp", maintain_order=True)
    book = Book(b["timestamp"].to_numpy(), b["bid_price"].to_numpy(), b["bid_amount"].to_numpy(),
                b["ask_price"].to_numpy(), b["ask_amount"].to_numpy())
    tr = Trades(t["timestamp"].to_numpy(), np.where(t["side"].to_numpy() == "buy", 1, -1),
                t["price"].to_numpy(), t["amount"].to_numpy())
    del b, t
    return _finish(book, tr, snap)


def _finish(book, tr, snap):
    snap = snap.sort("timestamp", maintain_order=True)
    sts = snap["timestamp"].to_numpy()
    sd = {}
    for side in (1, -1):
        name = "bids" if side > 0 else "asks"
        px = np.column_stack([snap[f"{name}[{i}].price"].to_numpy() for i in range(5)]) * side
        q = np.column_stack([snap[f"{name}[{i}].amount"].to_numpy() for i in range(5)])
        sd[side] = (px, q)
    del snap
    gc.collect()                    # a busy day is several GB, keep only the arrays
    S = {}
    for side in (1, -1):
        # the rows where my side changed, as in prep_day. Compared on the stored arrays, then the kept
        # rows are signed and widened, which gives the same numbers with less memory on a busy day
        px = book.bid_px if side > 0 else book.ask_px
        qq = book.bid_qty if side > 0 else book.ask_qty
        ch = np.ones(len(px), bool)
        ch[1:] = (px[1:] != px[:-1]) | (qq[1:] != qq[:-1])
        idx = np.flatnonzero(ch)
        del ch
        opp = tr.side == -side
        S[side] = dict(tick_ts=book.ts[idx], tick_px=px[idx] * side, tick_q=qq[idx].astype(float),
                       tr_ts=tr.ts[opp], tr_px=tr.px[opp] * side, tr_q=tr.qty[opp],
                       snap_ts=sts, snap_px=sd[side][0], snap_q=sd[side][1])
    return book, tr, S
