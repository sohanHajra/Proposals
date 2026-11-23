"""Loader for Bybit's free BTCUSDT linear files (secondary, out of venue).

Book  quote-saver.bycsi.com/orderbook/linear/BTCUSDT/DAY_BTCUSDT_ob200.data.zip, one JSON line per
      message of the orderbook.200 feed, a snapshot then deltas about every 100 ms. "cts" is the
      matching engine time and "ts" the time the message was sent. Size "0" deletes a level.
      Updates chain on data.u, one apart. A break makes the book untrusted until the next snapshot.
Trades public.bybit.com/trading/BTCUSDT/BTCUSDTDAY.csv.gz, timestamp in seconds, side Buy or Sell
      for the taker, size, price, trdMatchID.

Written as the same three parquet files as s2fb.cryptostruct, times in microseconds. The book's
exchange time is cts, so book and trades sit on the matching engine clock. local_timestamp is ts,
since the file holds no capture time. A top of book row is written for every message, changed or
not, so a quiet book is not mistaken for a feed gap by the gap rule or by the 01 decision code,
which both read gaps from the top of book times. A five level row is written each time the top five
change.

Usage  python -m s2fb.bybit DAY
"""
import gzip
import json
import sys
import time
import zipfile

import polars as pl

from .paths import RAW, DERIVED
from .cryptostruct import Sink, Side, TICKER, SNAP5, TRADES

OUT = DERIVED / "bybit"
TICK = 0.1


def out_file(day, sym, kind):
    ext = "json" if kind == "meta" else "parquet"
    return OUT / f"{day}_{sym}_{kind}.{ext}"


def book_file(day, sym="BTCUSDT"):
    return RAW / "bybit" / f"{day}_{sym}_ob200.data.zip"


def trade_file(day, sym="BTCUSDT"):
    return RAW / "bybit" / f"{sym}{day}.csv.gz"


def convert(day, sym="BTCUSDT"):
    from .guard import check_load_allowed
    check_load_allowed(day, sym, "bybit")
    t0 = time.time()
    tk = Sink(out_file(day, sym, "ticker"), TICKER)
    sn = Sink(out_file(day, sym, "snap5"), SNAP5)
    bids, asks = Side(1), Side(-1)
    meta = dict(day=day, symbol=sym, book_file=book_file(day, sym).name, trade_file=trade_file(day, sym).name,
                messages=0, snapshots=[], chain_breaks=[], messages_untrusted=0, crossed_rows=0, rows_short_of_five=0)
    last_u = None; trusted = False; prev5 = None
    z = zipfile.ZipFile(book_file(day, sym))
    with z.open(z.namelist()[0]) as f:
        for ln in f:
            a = json.loads(ln)
            meta["messages"] += 1
            d = a["data"]
            if a["type"] == "snapshot":
                bids.reset(); asks.reset()
                trusted = True
                meta["snapshots"].append([a["ts"], d["u"]])
            elif last_u is not None and d["u"] != last_u + 1:
                meta["chain_breaks"].append([a["ts"], last_u, d["u"]])
                trusted = False
            last_u = d["u"]
            for side, lv in ((bids, d.get("b", [])), (asks, d.get("a", []))):
                for p, q in lv:
                    side.set(round(float(p) / TICK), float(p), float(q))
            if a["type"] == "snapshot":
                bids.rebuild_best(); asks.rebuild_best()
            if not trusted:
                meta["messages_untrusted"] += 1; continue
            ets, lts = a["cts"] * 1000, a["ts"] * 1000
            tb, ta = bids.top5(), asks.top5()
            if not tb or not ta:
                continue
            top = (bids.px[tb[0]], bids.q[tb[0]], asks.px[ta[0]], asks.q[ta[0]])
            tk.add(ets, lts, top[0], top[1], top[2], top[3])
            cur = (tuple((bids.px[t], bids.q[t]) for t in tb), tuple((asks.px[t], asks.q[t]) for t in ta))
            if cur == prev5:
                continue
            prev5 = cur
            if len(tb) < 5 or len(ta) < 5:
                meta["rows_short_of_five"] += 1; continue
            if top[0] >= top[2]:
                meta["crossed_rows"] += 1
            vals = []
            for i in range(5):
                vals += [cur[1][i][0], cur[1][i][1], cur[0][i][0], cur[0][i][1]]
            sn.add(ets, lts, *vals)
    tk.close(); sn.close()
    tr = pl.read_csv(trade_file(day, sym), columns=["timestamp", "side", "size", "price", "trdMatchID"],
                     schema_overrides={"timestamp": pl.Float64, "size": pl.Float64, "price": pl.Float64})
    us = (tr["timestamp"] * 1e6).round(0).cast(pl.Int64)
    out = pl.DataFrame({"timestamp": us, "local_timestamp": us, "id": tr["trdMatchID"].cast(pl.Utf8),
                        "side": tr["side"].str.to_lowercase(), "price": tr["price"], "amount": tr["size"]})
    OUT.mkdir(parents=True, exist_ok=True)
    out.write_parquet(out_file(day, sym, "trades"))
    meta.update(ticker_rows=tk.n, snap5_rows=sn.n, trade_rows=out.height,
                trade_sides=sorted(set(out["side"].to_list())), seconds=round(time.time() - t0, 1))
    out_file(day, sym, "meta").write_text(json.dumps(meta, indent=1))
    return meta


def converted(day, sym="BTCUSDT"):
    return all(out_file(day, sym, k).exists() for k in ("ticker", "trades", "snap5", "meta"))


if __name__ == "__main__":
    day = sys.argv[1]
    m = convert(day)
    print(json.dumps({k: v for k, v in m.items() if k not in ("snapshots", "chain_breaks")}, indent=1))
