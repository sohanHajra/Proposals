"""Replay sanity check on one day. Do trades print where the book said they would.

For each trade, the previous book update is the last update stamped strictly before the trade
(trades go before book updates inside one timestamp, as the replay orders them).
Writes results/replay/sanity_<day>.json.
"""
import json
import sys
import numpy as np

from .paths import ROOT
from .replay import load_day


def sanity(book, tr):
    k_prev = np.searchsorted(book.ts, tr.ts, side="left") - 1     # strictly earlier update
    k_incl = np.searchsorted(book.ts, tr.ts, side="right") - 1    # includes an update at the same stamp
    buy = (tr.side > 0) & (k_prev >= 0)
    sell = (tr.side < 0) & (k_prev >= 0)
    kb, ks = k_prev[buy], k_prev[sell]
    buy_incl = (tr.side > 0) & (k_incl >= 0)
    return dict(
        book_rows=int(len(book.ts)),
        trade_rows=int(len(tr.ts)),
        book_sorted=bool((np.diff(book.ts) >= 0).all()),
        trades_sorted=bool((np.diff(tr.ts) >= 0).all()),
        buy_trade_px_equals_prior_ask=float((tr.px[buy] == book.ask_px[kb]).mean()),
        buy_trade_px_ge_prior_ask=float((tr.px[buy] >= book.ask_px[kb]).mean()),
        buy_trade_px_equals_ask_incl_same_ts_update=float((tr.px[buy_incl] == book.ask_px[k_incl[buy_incl]]).mean()),
        sell_trade_px_equals_prior_bid=float((tr.px[sell] == book.bid_px[ks]).mean()),
    )


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    book, tr = load_day(day)
    res = sanity(book, tr)
    out = ROOT / "results" / "replay"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"sanity_{day}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
