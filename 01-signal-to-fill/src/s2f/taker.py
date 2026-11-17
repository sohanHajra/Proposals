"""Taker leg on the dev day. Paired design, every decision replayed at every delay.

Shortfall S(d) = side * (fill px - mid at t) / mid at t * 1e4 (top of book fill, see flags).
Drift = side * (mid at t+d - mid at t), arrival = side * (fill px - mid at t+d), both in bps.
Latency cost dS(d) = S(d) - S(1 ms). Slope of dS on log(d), 5 minute block bootstrap.
"""
import json
import sys
import numpy as np

from .paths import ROOT
from .replay import load_day, mid_at, book_index_at

DELAYS_MS = np.array([1, 2, 5, 10, 25, 50, 100, 250, 500])
SEED = 20261115
QTY = 0.01
BLOCK_US = 5 * 60 * 10**6


def make_decisions(book, mean_gap_s=10.0, seed=SEED, margin_s=60):
    rng = np.random.default_rng(seed)
    t0, t1 = book.ts[0], book.ts[-1]
    n = int((t1 - t0) / 1e6 / mean_gap_s * 1.3)
    gaps = rng.exponential(mean_gap_s * 1e6, n)
    t = t0 + np.cumsum(gaps)
    t = t[t < t1 - 600e6].astype(np.int64)
    side = rng.choice([-1, 1], size=len(t))
    # drop decisions within margin of any feed gap over 1 s
    d = np.diff(book.ts)
    gi = np.where(d > 1e6)[0]
    keep = np.ones(len(t), bool)
    for g in gi:
        lo, hi = book.ts[g] - margin_s * 1e6, book.ts[g + 1] + margin_s * 1e6
        keep &= ~((t >= lo) & (t <= hi))
    return t[keep], side[keep], len(gi)


def run(day="2026-09-01", tie_after=True, shuffle=False):
    book, tr = load_day(day)
    t, side, ngaps = make_decisions(book)
    n = len(t)
    nd = len(DELAYS_MS)
    mid0 = np.array([mid_at(book, x, True) for x in t])
    S = np.zeros((n, nd)); drift = np.zeros((n, nd)); arr = np.zeros((n, nd))
    flagged = np.zeros((n, nd), bool)
    for j, dms in enumerate(DELAYS_MS):
        ta = t + int(dms) * 1000
        k = book_index_at(book, ta, tie_after)
        ok = k >= 0
        kk = np.where(ok, k, 0)
        px = np.where(side > 0, book.ask_px[kk], book.bid_px[kk])
        av = np.where(side > 0, book.ask_qty[kk], book.bid_qty[kk])
        midd = 0.5 * (book.bid_px[kk] + book.ask_px[kk])
        S[:, j] = side * (px - mid0) / mid0 * 1e4
        drift[:, j] = side * (midd - mid0) / mid0 * 1e4
        arr[:, j] = side * (px - midd) / mid0 * 1e4
        flagged[:, j] = av < QTY
    dS = S - S[:, [0]]
    if shuffle:
        rng = np.random.default_rng(SEED + 1)
        for i in range(n):
            dS[i] = dS[i, rng.permutation(nd)]
    return dict(t=t, side=side, mid0=mid0, S=S, drift=drift, arr=arr, dS=dS,
                flagged=flagged, book=book, ngaps=ngaps)


def slope_blocks(dS, t, nboot=2000, seed=SEED):
    x = np.log(DELAYS_MS.astype(float)); xc = x - x.mean(); sxx = (xc ** 2).sum()
    per = (dS * xc).sum(1)
    blk = ((t - t.min()) // BLOCK_US).astype(int)
    ub, inv = np.unique(blk, return_inverse=True)
    bsum = np.bincount(inv, per); bn = np.bincount(inv)
    est = per.sum() / (len(t) * sxx)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(ub), (nboot, len(ub)))
    boots = bsum[idx].sum(1) / (bn[idx].sum(1) * sxx)
    return float(est), [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]


def mean_ci(v, t, nboot=2000, seed=SEED):
    blk = ((t - t.min()) // BLOCK_US).astype(int)
    ub, inv = np.unique(blk, return_inverse=True)
    bs = np.bincount(inv, v); bn = np.bincount(inv)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(ub), (nboot, len(ub)))
    b = bs[idx].sum(1) / bn[idx].sum(1)
    return float(v.mean()), [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def summarize(r, label):
    t = r["t"]; side = r["side"]
    out = dict(label=label, n_decisions=int(len(t)), feed_gaps_over_1s=int(r["ngaps"]),
               share_buys=float((side > 0).mean()),
               flagged_share_by_delay_ms={int(d): float(r["flagged"][:, j].mean()) for j, d in enumerate(DELAYS_MS)})
    beta, ci = slope_blocks(r["dS"], t)
    out["slope_bps_per_logms"] = dict(est=beta, ci95=ci)
    out["by_delay"] = {}
    for j, d in enumerate(DELAYS_MS):
        m, c = mean_ci(r["dS"][:, j], t)
        out["by_delay"][int(d)] = dict(
            mean_dS_bps=m, ci95=c,
            mean_S_bps=float(r["S"][:, j].mean()),
            mean_drift_bps=float(r["drift"][:, j].mean()),
            mean_arrival_bps=float(r["arr"][:, j].mean()),
            drift_minus_drift1=float((r["drift"][:, j] - r["drift"][:, 0]).mean()),
            arrival_minus_arrival1=float((r["arr"][:, j] - r["arr"][:, 0]).mean()))
    # H1b split by sign of side * (mid at t+1s - mid at t)
    m1 = np.array([mid_at(r["book"], x + 10**6, True) for x in t])
    pos = side * (m1 - r["mid0"]) > 0
    j100 = list(DELAYS_MS).index(100)
    a = r["dS"][:, j100]
    out["H1b_dS100"] = dict(share_positive=float(pos.mean()),
        mean_pos=float(a[pos].mean()), mean_rest=float(a[~pos].mean()))
    # tail share
    s = r["dS"][:, j100]
    top = np.sort(s)[::-1][: max(1, int(0.1 * len(s)))]
    out["tail_share_worst10pct_dS100"] = float(top.sum() / s.sum()) if s.sum() != 0 else None
    return out


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    res = {}
    res["primary_tie_after"] = summarize(run(day, True), "tie after (primary)")
    res["tie_before"] = summarize(run(day, False), "tie before (flipped)")
    res["placebo_shuffled"] = summarize(run(day, True, shuffle=True), "delay labels shuffled")
    out = ROOT / "results" / "taker"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"taker_dev_{day}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: (v["slope_bps_per_logms"], v["by_delay"][500]["mean_dS_bps"], v["flagged_share_by_delay_ms"][500]) for k, v in res.items()}, indent=1))
