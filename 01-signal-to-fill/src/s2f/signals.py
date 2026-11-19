"""Signal decisions (secondary, preregistered), as specified on 2026-11-19 before any were run.

The book seen at a stamp is the last ticker row with that exchange time, so the imbalance is read
on those rows only. I = (bid size - ask size) / (bid size + ask size).
The threshold is the 90th percentile of |I| over those rows on the dev day. It is computed once
here and stored with the results, then frozen for the test days.
A decision fires at a row with |I| at or above the threshold, at that row's exchange time, with side
equal to the sign of I. After a decision the next one can fire only at a row at least 1 s later.
Decisions within 60 s of a feed gap over 1 s, or in the last 600 s of the file, are dropped, as for
the random decisions.
"""
import numpy as np

QUANTILE = 0.9
MIN_GAP_US = 10**6


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


def make_signal_decisions(book, thr=None):
    """Returns t, side, number of feed gaps, threshold used."""
    if thr is None:
        thr = threshold(book)
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
