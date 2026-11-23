"""Loader for CryptoStruct day files (binance_swap-SYM-DAY.txt.zst).

Format, as read on cryptostruct.com (day-file-format reference) on 2026-11-23 and checked on the
2026-09-01 file only. Line 1 is the instrument header (JSON object). Every other line is
  [msgType, instrumentId, prevEventId, eventId, adapterTs, exchangeTs, data, ...]
with times in integer ns since epoch. Types used here
  0  book snapshot, [[side, price, qty, count], ...], resets the book
  1  book update, same shape, qty replaces the level and "0" deletes it
  2  trades, [[side, price, qty, tradeId, exchangeTradeTs], ...], side is the aggressor
  5  instrument state, [5, id, adapterTs, state, message]
  6  top of book, at most one level per side
side 0 is bid or buy, 1 is ask or sell. Prices and sizes are decimal strings.

The file runs from about 23:52 the day before to about 00:01 the day after. I keep the rows whose
adapterTs falls in [00:00, 24:00) UTC of the day, the way the Tardis files are cut by their local
capture time. The book is built from the first snapshot in the file, so it is warm at midnight.

Output goes to data/derived/cryptostruct as three parquet files per day with the same columns as
the Tardis files 01 reads (times in microseconds), plus a json with counts:
  ticker   timestamp, local_timestamp, bid_price, bid_amount, ask_price, ask_amount  (type 6)
  trades   timestamp, local_timestamp, id, side, price, amount  (type 2, one row per fill,
           timestamp is the fill's own exchange time)
  snap5    timestamp, local_timestamp, bids[i].price, bids[i].amount, asks[i].price, asks[i].amount
           for i in 0..4, one row each time the top five levels change after a type 0 or 1 line.
           Built from the depth stream. Lines with exchangeTs 0 (REST snapshots) change the book but
           write no row, so the next update writes it. After a broken event chain or an ERROR state
           the book is not trusted and no row is written until the next snapshot.

Usage  python -m s2fb.cryptostruct DAY [SYM] tt|depth
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from .paths import RAW, DERIVED

CHUNK = 2_000_000
OUT = DERIVED / "cryptostruct"


def raw_file(day, sym="BTCUSDT"):
    return RAW / "cryptostruct" / f"binance_swap-{sym}-{day}.txt.zst"


def out_file(day, sym, kind):
    ext = "json" if kind == "meta_tt" or kind == "meta_depth" else "parquet"
    return OUT / f"{day}_{sym}_{kind}.{ext}"


def day_window_ns(day):
    d0 = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    a = int(d0.timestamp()) * 10**9
    return a, a + 86400 * 10**9


def lines(path):
    """Stream the decompressed file line by line. The header comes first."""
    p = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE, bufsize=1 << 24)
    try:
        for ln in p.stdout:
            yield ln
    finally:
        p.stdout.close()
        rc = p.wait()
        if rc != 0:
            raise RuntimeError(f"zstd exited with {rc} on {path}")


class Sink:
    """Collects columns in chunks and appends them to one parquet file."""

    def __init__(self, path, schema):
        self.path = path; self.schema = schema
        self.cols = {f.name: [] for f in schema}
        self.writer = None; self.n = 0

    def add(self, *vals):
        for c, v in zip(self.cols.values(), vals):
            c.append(v)
        if len(next(iter(self.cols.values()))) >= CHUNK:
            self.flush()

    def flush(self):
        k = len(next(iter(self.cols.values())))
        if k == 0:
            return
        tbl = pa.table({n: pa.array(v, type=self.schema.field(n).type) for n, v in self.cols.items()})
        if self.writer is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.writer = pq.ParquetWriter(str(self.path) + ".part", self.schema)
        self.writer.write_table(tbl)
        self.n += k
        for v in self.cols.values():
            v.clear()

    def close(self):
        self.flush()
        if self.writer is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.writer = pq.ParquetWriter(str(self.path) + ".part", self.schema)
        self.writer.close()
        (self.path.parent / (self.path.name + ".part")).rename(self.path)


TICKER = pa.schema([("timestamp", pa.int64()), ("local_timestamp", pa.int64()),
                    ("bid_price", pa.float64()), ("bid_amount", pa.float64()),
                    ("ask_price", pa.float64()), ("ask_amount", pa.float64())])
TRADES = pa.schema([("timestamp", pa.int64()), ("local_timestamp", pa.int64()), ("id", pa.string()),
                    ("side", pa.string()), ("price", pa.float64()), ("amount", pa.float64())])
SNAP_COLS = [f"{s}[{i}].{f}" for i in range(5) for s in ("asks", "bids") for f in ("price", "amount")]
SNAP5 = pa.schema([("timestamp", pa.int64()), ("local_timestamp", pa.int64())] +
                  [(c, pa.float64()) for c in SNAP_COLS])


def header(path):
    """The first line only. zstd is stopped once it is read."""
    p = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    ln = p.stdout.readline()
    p.kill(); p.wait(); p.stdout.close()
    return json.loads(ln)


def convert_tt(day, sym="BTCUSDT"):
    """Top of book (type 6), trades (type 2) and state lines (type 5)."""
    from .guard import check_load_allowed
    check_load_allowed(day, sym, "cryptostruct")
    path = raw_file(day, sym)
    lo, hi = day_window_ns(day)
    tk = Sink(out_file(day, sym, "ticker"), TICKER)
    tr = Sink(out_file(day, sym, "trades"), TRADES)
    meta = dict(day=day, symbol=sym, file=path.name, window_adapter_ns=[lo, hi], lines_by_type={},
                ticker_lines_one_side=0, ticker_lines_no_side=0, ticker_rows_out_of_window=0,
                trade_lines_out_of_window=0, trade_fills=0, states=[], exchange_ts_zero={})
    bid = ask = None
    first = True
    t0 = time.time()
    for ln in lines(path):
        if first:
            meta["header"] = json.loads(ln)["instrument"]; first = False; continue
        typ = ln[1:ln.index(b",")].decode()
        meta["lines_by_type"][typ] = meta["lines_by_type"].get(typ, 0) + 1
        if typ not in ("6", "2", "5"):
            continue
        a = json.loads(ln)
        if typ == "5":
            meta["states"].append([a[2], a[3], a[4]]); continue
        ats, ets = a[4], a[5]
        if ets == 0:
            meta["exchange_ts_zero"][typ] = meta["exchange_ts_zero"].get(typ, 0) + 1
        if typ == "6":
            got = 0
            for side, p, q, _ in a[6]:
                if side == 0:
                    bid = (float(p), float(q))
                else:
                    ask = (float(p), float(q))
                got += 1
            if got == 1:
                meta["ticker_lines_one_side"] += 1
            elif got == 0:
                meta["ticker_lines_no_side"] += 1
            if not (lo <= ats < hi):
                meta["ticker_rows_out_of_window"] += 1; continue
            if bid is None or ask is None:
                continue
            tk.add(ets // 1000, ats // 1000, bid[0], bid[1], ask[0], ask[1])
        else:
            if not (lo <= ats < hi):
                meta["trade_lines_out_of_window"] += 1; continue
            for side, p, q, tid, fts in a[6]:
                tr.add(fts // 1000, ats // 1000, str(tid), "buy" if side == 0 else "sell", float(p), float(q))
                meta["trade_fills"] += 1
    tk.close(); tr.close()
    meta["ticker_rows"] = tk.n; meta["trade_rows"] = tr.n
    meta["seconds"] = round(time.time() - t0, 1)
    out_file(day, sym, "meta_tt").write_text(json.dumps(meta, indent=1))
    return meta


class Side:
    """One side of the book keyed by integer tick. sign +1 for bids (best is the highest tick)."""

    SCAN = 5000

    def __init__(self, sign):
        self.sign = sign; self.q = {}; self.px = {}; self.best = None

    def reset(self):
        self.q.clear(); self.px.clear(); self.best = None

    def set(self, tick, px, qty):
        if qty == 0.0:
            if tick in self.q:
                del self.q[tick]
                if tick == self.best:
                    self._find_best(tick)
        else:
            self.q[tick] = qty; self.px[tick] = px
            if self.best is None or (tick - self.best) * self.sign > 0:
                self.best = tick

    def _find_best(self, start):
        s = self.sign
        for k in range(1, self.SCAN):
            t = start - s * k
            if t in self.q:
                self.best = t; return
        self.best = (max(self.q) if s > 0 else min(self.q)) if self.q else None

    def rebuild_best(self):
        self.best = (max(self.q) if self.sign > 0 else min(self.q)) if self.q else None

    def top5(self):
        out = []
        if self.best is None:
            return out
        s = self.sign; t = self.best; k = 0
        while len(out) < 5 and k < self.SCAN:
            tt = t - s * k
            if tt in self.q:
                out.append(tt)
            k += 1
        if len(out) < 5 and len(self.q) > len(out):
            out = sorted(self.q, reverse=s > 0)[:5]
        return out


def convert_depth(day, sym="BTCUSDT"):
    """Five level snapshots from the depth stream (types 0 and 1), plus state lines (type 5)."""
    from .guard import check_load_allowed
    check_load_allowed(day, sym, "cryptostruct")
    path = raw_file(day, sym)
    lo, hi = day_window_ns(day)
    hd = header(path)["instrument"]
    tick = float(hd["ticksize"])
    sink = Sink(out_file(day, sym, "snap5"), SNAP5)
    bids, asks = Side(1), Side(-1)
    meta = dict(day=day, symbol=sym, ticksize=tick, snapshots=[], chain_breaks=[], states=[],
                update_lines=0, update_levels=0, lines_no_row_untrusted=0, lines_exchange_ts_zero=0,
                rows=0, crossed_rows=0, levels_at_snapshot=[])
    last_id = None; trusted = False; prev = None
    t0 = time.time(); first = True
    for ln in lines(path):
        if first:
            first = False; continue
        c = ln[1:3]
        if c == b"5,":
            a = json.loads(ln)
            meta["states"].append([a[2], a[3], a[4]])
            if a[3] == "ERROR":
                trusted = False
            continue
        if c != b"0," and c != b"1,":
            continue
        a = json.loads(ln)
        ats, ets = a[4], a[5]
        if a[0] == 0:
            bids.reset(); asks.reset()
            for side, p, q, _ in a[6]:
                (bids if side == 0 else asks).set(round(float(p) / tick), float(p), float(q))
            bids.rebuild_best(); asks.rebuild_best()
            meta["snapshots"].append([ats, ets, len(bids.q), len(asks.q)])
            last_id = a[3]; trusted = True
        else:
            meta["update_lines"] += 1
            if a[2] != last_id:
                meta["chain_breaks"].append([ats, a[2], last_id])
                trusted = False
            last_id = a[3]
            for side, p, q, _ in a[6]:
                (bids if side == 0 else asks).set(round(float(p) / tick), float(p), float(q))
                meta["update_levels"] += 1
        if not (lo <= ats < hi):
            continue
        if not trusted:
            meta["lines_no_row_untrusted"] += 1; continue
        if ets == 0:
            meta["lines_exchange_ts_zero"] += 1; continue
        tb, ta = bids.top5(), asks.top5()
        cur = (tuple((bids.px[t], bids.q[t]) for t in tb), tuple((asks.px[t], asks.q[t]) for t in ta))
        if cur == prev:
            continue
        prev = cur
        if len(tb) < 5 or len(ta) < 5:
            meta.setdefault("rows_short_of_five", 0)
            meta["rows_short_of_five"] += 1
            continue
        if cur[0][0][0] >= cur[1][0][0]:
            meta["crossed_rows"] += 1
        vals = []
        for i in range(5):
            vals += [cur[1][i][0], cur[1][i][1], cur[0][i][0], cur[0][i][1]]
        sink.add(ets // 1000, ats // 1000, *vals)
    sink.close()
    meta["rows"] = sink.n
    meta["seconds"] = round(time.time() - t0, 1)
    out_file(day, sym, "meta_depth").write_text(json.dumps(meta, indent=1))
    return meta


def converted(day, sym="BTCUSDT"):
    return all(out_file(day, sym, k).exists() for k in ("ticker", "trades", "snap5", "meta_tt", "meta_depth"))


if __name__ == "__main__":
    day = sys.argv[1]
    sym = sys.argv[2] if len(sys.argv) > 3 else "BTCUSDT"
    what = sys.argv[-1]
    m = convert_tt(day, sym) if what == "tt" else convert_depth(day, sym)
    print(json.dumps({k: v for k, v in m.items() if k not in ("snapshots", "states", "chain_breaks", "header")}, indent=1))
