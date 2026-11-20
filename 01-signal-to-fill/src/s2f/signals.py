"""Signal decisions (secondary, preregistered), as specified on 2026-11-19 before any were run.

The book seen at a stamp is the last ticker row with that exchange time, so the imbalance is read
on those rows only. I = (bid size - ask size) / (bid size + ask size).
The threshold is the 90th percentile of |I| over those rows on the dev day. It was computed once on
2026-11-19 and stored in results/taker/followups_dev_2026-09-01.json (signal.threshold_abs_imbalance).
Every run, dev day included, reads that stored value. Nothing recomputes it.
A decision fires at a row with |I| at or above the threshold, at that row's exchange time, with side
equal to the sign of I. After a decision the next one can fire only at a row at least 1 s later.
Decisions within 60 s of a feed gap over 1 s, or in the last 600 s of the file, are dropped, as for
the random decisions.
"""
import json

import numpy as np

from .paths import RESULTS

QUANTILE = 0.9
MIN_GAP_US = 10**6
FROZEN_FILE = RESULTS / "taker" / "followups_dev_2026-09-01.json"
FROZEN_KEY = ("signal", "threshold_abs_imbalance")


def frozen_threshold(path=None):
    """The dev day threshold as stored. Fails loudly if the file or the field is missing."""
    p = FROZEN_FILE if path is None else path
    if not p.exists():
        raise FileNotFoundError(f"frozen signal threshold file missing: {p}. Refusing to recompute it.")
    d = json.loads(p.read_text())
    try:
        v = d[FROZEN_KEY[0]][FROZEN_KEY[1]]
    except KeyError:
        raise KeyError(f"{p} has no {'.'.join(FROZEN_KEY)}. Refusing to recompute it.")
    v = float(v)
    if not (0.0 < v <= 1.0):
        raise ValueError(f"stored signal threshold {v} is not a valid |I| quantile")
    return v


def last_row_per_stamp(ts):
    keep = np.ones(len(ts), bool)
    keep[:-1] = ts[1:] != ts[:-1]
    return np.where(keep)[0]


def imbalance(bid_q, ask_q):
    b = bid_q.astype(float); a = ask_q.astype(float)
    s = b + a
    return np.where(s > 0, (b - a) / np.where(s > 0, s, 1.0), 0.0)


def threshold(book, q=QUANTILE):
    r = last_row_per_stamp(book.ts)
    return float(np.quantile(np.abs(imbalance(book.bid_qty[r], book.ask_qty[r])), q))


def first_per_gap(ts, min_gap=MIN_GAP_US):
    """Greedy forward pass. Keep a time, then skip everything closer than min_gap to it."""
    out = []
    nxt = -np.inf
    i = 0
    n = len(ts)
    while i < n:
        if ts[i] >= nxt:
            out.append(i)
            nxt = ts[i] + min_gap
            i = np.searchsorted(ts, nxt, "left")
        else:
            i += 1
    return np.array(out, dtype=np.int64)


def drop_near_gaps(book, t, margin_s=60, end_cut_s=600):
    keep = t < book.ts[-1] - end_cut_s * 10**6
    d = np.diff(book.ts)
    gi = np.where(d > 10**6)[0]
    for g in gi:
        lo, hi = book.ts[g] - margin_s * 10**6, book.ts[g + 1] + margin_s * 10**6
        keep &= ~((t >= lo) & (t <= hi))
    return keep, len(gi)


def make_signal_decisions(book, thr):
    """Returns t, side, number of feed gaps, threshold used. thr must be given (the frozen value)."""
    if thr is None:
        raise ValueError("signal decisions need the frozen dev day threshold, it is never recomputed")
    r = last_row_per_stamp(book.ts)
    I = imbalance(book.bid_qty[r], book.ask_qty[r])
    hit = r[(np.abs(I) >= thr) & (I != 0)]
    ts = book.ts[hit]
    pick = first_per_gap(ts)
    rows = hit[pick]
    t = book.ts[rows].astype(np.int64)
    side = np.sign(imbalance(book.bid_qty[rows], book.ask_qty[rows])).astype(int)
    keep, ngaps = drop_near_gaps(book, t)
    return t[keep], side[keep], ngaps, thr
