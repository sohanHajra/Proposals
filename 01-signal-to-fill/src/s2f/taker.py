"""Taker leg. Paired design, every decision replayed at every delay.

H1 is judged on the five level walk (registered, restored by the Deviation of 2026-11-19 near
midnight). The top of book fill is reported next to it as a robustness line.
Shortfall S(d) = side * (fill px - mid at t) / mid at t * 1e4.
Drift = side * (mid at t+d - mid at t), arrival = side * (fill px - mid at t+d), both in bps.
Latency cost dS(d) = S(d) - S(1 ms). Slope of dS on log(d), 5 minute block bootstrap.
"""
import json
import sys
import numpy as np

from .paths import ROOT, result_path, guard_day
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


def slope_blocks(dS, t, nboot=2000, seed=SEED, block_us=BLOCK_US):
    x = np.log(DELAYS_MS.astype(float)); xc = x - x.mean(); sxx = (xc ** 2).sum()
    per = (dS * xc).sum(1)
    blk = ((t - t.min()) // block_us).astype(int)
    ub, inv = np.unique(blk, return_inverse=True)
    bsum = np.bincount(inv, per); bn = np.bincount(inv)
    est = per.sum() / (len(t) * sxx)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(ub), (nboot, len(ub)))
    boots = bsum[idx].sum(1) / (bn[idx].sum(1) * sxx)
    return float(est), [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]


def mean_ci(v, t, nboot=2000, seed=SEED, block_us=BLOCK_US):
    blk = ((t - t.min()) // block_us).astype(int)
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


def shuffle_rows(dS):
    """Placebo. Delay labels shuffled within each decision, same draws as in run()."""
    out = dS.copy()
    rng = np.random.default_rng(SEED + 1)
    for i in range(len(out)):
        out[i] = out[i, rng.permutation(out.shape[1])]
    return out


def walk_summary(dS, S, flag, t, label):
    beta, ci = slope_blocks(dS, t)
    out = dict(label=label, n_decisions=int(len(t)),
               flagged_share_by_delay_ms={int(d): float(flag[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
               slope_bps_per_logms=dict(est=beta, ci95=ci), by_delay={})
    for j, d in enumerate(DELAYS_MS):
        m, c = mean_ci(dS[:, j], t)
        out["by_delay"][int(d)] = dict(mean_dS_bps=m, ci95=c, mean_S_bps=float(S[:, j].mean()))
    return out


def walk_results(day):
    """H1 under the five level walk, with the tie flip and the placebo on the same fill."""
    from .passive import prep_day
    from .taker_followups import taker_arrays
    book, tr, S = prep_day(day)
    t, side, _ = make_decisions(book)
    a = taker_arrays(book, S, t, side, True)
    b = taker_arrays(book, S, t, side, False)
    return {"primary_five_level_walk": walk_summary(a["dS_walk"], a["S_walk"], a["flag_walk"], t, "five level walk, tie after (H1 primary)"),
            "tie_before_five_level_walk": walk_summary(b["dS_walk"], b["S_walk"], b["flag_walk"], t, "five level walk, tie before (flipped)"),
            "placebo_shuffled_five_level_walk": walk_summary(shuffle_rows(a["dS_walk"]), a["S_walk"], a["flag_walk"], t, "five level walk, delay labels shuffled")}


def results(day):
    res = {}
    res["primary_tie_after"] = summarize(run(day, True), "tie after (top of book, robustness since 2026-11-19)")
    res["tie_before"] = summarize(run(day, False), "tie before (flipped)")
    res["placebo_shuffled"] = summarize(run(day, True, shuffle=True), "delay labels shuffled")
    res.update(walk_results(day))
    return res


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    guard_day(day)
    res = results(day)
    p = result_path("taker", "taker", day)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: (v["slope_bps_per_logms"], v["by_delay"][500]["mean_dS_bps"], v["flagged_share_by_delay_ms"][500]) for k, v in res.items()}, indent=1))
