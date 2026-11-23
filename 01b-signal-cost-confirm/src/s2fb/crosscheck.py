"""CryptoStruct against Tardis on 2026-09-01, the build day, before the loader is used for anything.

The preregistration asks for trade count, first and last trade, and the share of trades matching
on time, price and size. The agreement rule (Deviation of 2026-11-23, item 1): at least 99% of
trades match in each direction, each trade matched once at most. Matching is on the exchange time
of the trade in microseconds, price and size. The trade id match and the top of book comparison
are extra description and don't enter the rule.

Writes results/loader/crosscheck_2026-09-01.json.
"""
import json
import sys

import polars as pl

from .paths import RAW, RESULTS, BUILD_DAY
from .cryptostruct import out_file, converted

AGREE = 0.99


def tardis_trades(day, sym="BTCUSDT"):
    f = RAW / "tardis" / f"binance-futures_trades_{day}_{sym}.csv.gz"
    return pl.read_csv(f, columns=["timestamp", "local_timestamp", "id", "side", "price", "amount"],
                       schema_overrides={"id": pl.Utf8, "price": pl.Float64, "amount": pl.Float64})


def tardis_ticker(day, sym="BTCUSDT"):
    f = RAW / "tardis" / f"binance-futures_book_ticker_{day}_{sym}.csv.gz"
    return pl.read_csv(f, columns=["timestamp", "local_timestamp", "bid_price", "bid_amount", "ask_price", "ask_amount"],
                       schema_overrides={c: pl.Float64 for c in ("bid_price", "bid_amount", "ask_price", "ask_amount")})


def multiset_match(a, b, keys):
    """Number of rows of a and of b that can be paired one to one on keys."""
    ca = a.group_by(keys).agg(pl.len().alias("na"))
    cb = b.group_by(keys).agg(pl.len().alias("nb"))
    j = ca.join(cb, on=keys, how="inner")
    return int(j.select(pl.min_horizontal("na", "nb")).sum().item())


def row(df, i):
    r = df.row(i, named=True)
    return {k: r[k] for k in ("timestamp", "id", "side", "price", "amount")}


def compare(day=BUILD_DAY, sym="BTCUSDT"):
    if day != BUILD_DAY:
        raise SystemExit("the loader check runs on the build day only")
    if not converted(day, sym):
        raise SystemExit("convert the CryptoStruct day first (python -m s2fb.cryptostruct DAY tt and depth)")
    tz = tardis_trades(day, sym)
    cs = pl.read_parquet(out_file(day, sym, "trades"))
    # file order sorted by exchange time, stable, as 01 reads them
    tz = tz.sort("timestamp", maintain_order=True)
    cs = cs.sort("timestamp", maintain_order=True)
    keys = ["timestamp", "price", "amount"]
    m = multiset_match(tz, cs, keys)
    m_side = multiset_match(tz, cs, keys + ["side"])
    ids_t = set(tz["id"].to_list()); ids_c = set(cs["id"].to_list())
    res = dict(day=day, symbol=sym, agreement_rule=f"at least {AGREE:.0%} matched each way on time, price and size",
               trades_tardis=tz.height, trades_cryptostruct=cs.height,
               count_difference=cs.height - tz.height,
               first_trade_tardis=row(tz, 0), first_trade_cryptostruct=row(cs, 0),
               last_trade_tardis=row(tz, tz.height - 1), last_trade_cryptostruct=row(cs, cs.height - 1),
               matched_time_price_size=m,
               share_tardis_matched=m / tz.height, share_cryptostruct_matched=m / cs.height,
               matched_time_price_size_side=m_side,
               share_tardis_matched_with_side=m_side / tz.height,
               ids_in_both=len(ids_t & ids_c), ids_only_tardis=len(ids_t - ids_c), ids_only_cryptostruct=len(ids_c - ids_t),
               volume_tardis=float(tz["amount"].sum()), volume_cryptostruct=float(cs["amount"].sum()))
    res["agree"] = bool(res["share_tardis_matched"] >= AGREE and res["share_cryptostruct_matched"] >= AGREE)
    # description only
    tk = tardis_ticker(day, sym)
    ck = pl.read_parquet(out_file(day, sym, "ticker"))
    k2 = ["timestamp", "bid_price", "bid_amount", "ask_price", "ask_amount"]
    mt = multiset_match(tk, ck, k2)
    res["ticker_description"] = dict(rows_tardis=tk.height, rows_cryptostruct=ck.height, matched_all_five_fields=mt,
                                     share_tardis_matched=mt / tk.height, share_cryptostruct_matched=mt / ck.height)
    snap_t = RAW / "tardis" / f"binance-futures_book_snapshot_5_{day}_{sym}.csv.gz"
    nt = pl.scan_csv(snap_t).select(pl.len()).collect().item()
    nc = pl.scan_parquet(out_file(day, sym, "snap5")).select(pl.len()).collect().item()
    res["five_level_rows_description"] = dict(rows_tardis=nt, rows_cryptostruct=nc)
    p = RESULTS / "loader" / f"crosscheck_{day}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    r = compare(*(sys.argv[1:2] or [BUILD_DAY]))
    print(json.dumps({k: v for k, v in r.items()}, indent=1))
