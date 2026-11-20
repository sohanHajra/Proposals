"""Jump moment split and stale top of book count. Exploratory, added 2026-11-19, not a registered test.

Written and committed before any of it was run on data. Idea from reading Budish, Cramton and
Shim (2015). The thresholds below are frozen here for the test days, where this runs once after
the registered tests. It never changes H1 to H5, their tests or their verdicts.

Jump moment
  A ticker stamp tau is a jump stamp when |log mid(tau) - log mid(tau - W)| >= K bps, with the mid
  read on the last ticker row at or before each time. Direction is the sign of that move.
  Primary spec A is K = 2 bps, W = 10 ms. In their model a quote is picked off on a jump bigger
  than half the spread plus what it costs to take it. Half a one tick spread is under 0.01 bps here,
  so that part never binds. The lowest USDT taker fee on the Binance USD-M schedule is 0.017%
  (1.7 bps), so a move under that cannot pay even the cheapest taker who hits the old quote.
  K = 2 bps is that rounded up. W = 10 ms is their 2011 median arbitrage duration (7 ms) rounded up.
  Spec B is K = 5 bps, W = 10 ms (the regular taker fee, 0.05%).
  Spec C is K = 2 bps, W = 100 ms (their example batch interval), for slower moves.
  All three are run and reported. A is the one carried to the test days as the main line.

Decision window
  A decision at t is after a jump when some jump stamp lies in [t - 5 ms, t]. 5 ms is the low end of
  the delay grid where fast traders react (2 to 3 ms in Hasbrouck and Saar 2013, 7 ms median in
  Budish et al. 2011). Every jump stamp counts here, with no spacing.

Spaced jumps
  For the jump decisions and the stale count, one move should count once. Jumps are thinned to the
  first jump stamp, then nothing closer than 1 s after it (as for signal decisions). Jumps within
  60 s of a feed gap over 1 s, or in the last 600 s of the file, are dropped.

Latency cost
  Exactly as in H3. Top of book taker fill at t + d (tie after), dS(100 ms) = S(100 ms) - S(1 ms),
  S(d) = side * (fill px - mid at t) / mid at t * 1e4. Intervals are the 5 minute block bootstrap,
  2,000 resamples, seed 20261115.
  1. Random decisions after a jump minus the rest.
  2. Signal decisions after a jump minus the rest.
  3. Jump decisions. One per spaced jump at tau + u, u uniform in [0, 5000] microseconds (seed
     20261115 + 101). Side with the jump (buy after an up move, the side a sniper takes) and,
     on the same decisions, side against it. Each against random decisions outside the window,
     pooled in one bootstrap.

Stale top of book count
  At a spaced jump tau, take the touch a taker with the jump would hit (the ask after an up move)
  at tau, price p0. At tau + h, h in 1, 2, 5 ms, the level is gone when the touch on that side is
  now worse than p0 for that taker. A second line also counts it gone when the price is still p0
  but less than 0.01 BTC shows there. The same is done on the other side of the book, and at the
  random decisions with their own side as the baseline. Shares with intervals, jump minus baseline
  pooled in one bootstrap.

Too small to read
  A group with fewer than 30 decisions, or spread over fewer than 10 five minute blocks, is
  reported with its numbers and marked too small to read. No reading is made from it.
"""
import json
import os
import sys
import numpy as np

from .paths import ROOT, guard_day
from .replay import load_day, book_index_at
from .taker import DELAYS_MS, QTY, SEED, BLOCK_US, make_decisions
from .signals import make_signal_decisions, frozen_threshold, last_row_per_stamp, first_per_gap, drop_near_gaps
from .stats import group_diff, group_mean

SPECS = {
    "A": dict(k_bps=2.0, w_ms=10, primary=True),
    "B": dict(k_bps=5.0, w_ms=10, primary=False),
    "C": dict(k_bps=2.0, w_ms=100, primary=False),
}
WINDOW_MS = 5
STALE_H_MS = (1, 2, 5)
SPACING_US = 10**6
JUMP_SEED = SEED + 101
MIN_N = 30
MIN_BLOCKS = 10
J1 = list(DELAYS_MS).index(1)
J100 = list(DELAYS_MS).index(100)
CONFIG = dict(label="exploratory, added 2026-11-19, not a registered test", specs=SPECS,
              decision_window_ms=WINDOW_MS, stale_horizons_ms=list(STALE_H_MS), spacing_s=1,
              jump_seed=JUMP_SEED, min_n=MIN_N, min_blocks=MIN_BLOCKS, order_size_btc=QTY,
              cost="H3, top of book dS(100 ms), tie after", bootstrap="5 minute blocks, 2000, seed 20261115")


def mid_idx(book, k):
    return 0.5 * (book.bid_px[k] + book.ask_px[k])


def jump_stamps(book, k_bps, w_ms):
    """All jump stamps and their direction."""
    r = last_row_per_stamp(book.ts)
    ts = book.ts[r]
    m1 = mid_idx(book, r)
    k0 = book_index_at(book, ts - w_ms * 1000, True)
    ok = k0 >= 0
    m0 = mid_idx(book, np.maximum(k0, 0))
    mv = np.log(m1 / m0) * 1e4
    hit = ok & (np.abs(mv) >= k_bps)
    return ts[hit].astype(np.int64), np.sign(mv[hit]).astype(int), mv[hit]


def spaced(book, jts, jdir, jmv):
    if len(jts) == 0:
        return jts, jdir, jmv
    p = first_per_gap(jts, SPACING_US)
    t, d, m = jts[p], jdir[p], jmv[p]
    keep, _ = drop_near_gaps(book, t)
    return t[keep], d[keep], m[keep]


def after_jump(t, jts, window_ms=WINDOW_MS):
    if len(jts) == 0:
        return np.zeros(len(t), bool)
    i = np.searchsorted(jts, t, "right") - 1
    ok = i >= 0
    return ok & (jts[np.maximum(i, 0)] >= t - window_ms * 1000)


def dS_all(book, t, side):
    """dS(d) = S(d) - S(1 ms) for every delay, top of book, tie after, as in the taker leg."""
    k0 = np.maximum(book_index_at(book, t, True), 0)
    mid0 = mid_idx(book, k0)
    S = np.zeros((len(t), len(DELAYS_MS)))
    for j, dms in enumerate(DELAYS_MS):
        k = np.maximum(book_index_at(book, t + int(dms) * 1000, True), 0)
        px = np.where(side > 0, book.ask_px[k], book.bid_px[k])
        S[:, j] = side * (px - mid0) / mid0 * 1e4
    return S - S[:, [J1]]


def stale(book, t, side, h_ms):
    """Is the touch a taker on `side` would hit at t gone (worse for that taker) at t + h?
    Returns (gone, gone_or_below_order_size)."""
    k0 = np.maximum(book_index_at(book, t, True), 0)
    k1 = np.maximum(book_index_at(book, t + h_ms * 1000, True), 0)
    p0 = np.where(side > 0, book.ask_px[k0], book.bid_px[k0])
    p1 = np.where(side > 0, book.ask_px[k1], book.bid_px[k1])
    q1 = np.where(side > 0, book.ask_qty[k1], book.bid_qty[k1])
    gone = side * (p1 - p0) > 0
    thin = gone | ((p1 == p0) & (q1 < QTY))
    return gone, thin


def nblocks(t, mask):
    if mask.sum() == 0:
        return 0
    return int(len(np.unique((t[mask] - t.min()) // BLOCK_US)))


def readable(t, mask):
    n = int(mask.sum()); nb = nblocks(t, mask)
    return dict(n=n, n_blocks=nb, too_small_to_read=bool(n < MIN_N or nb < MIN_BLOCKS))


def pooled_diff(va, ta, vb, tb):
    """Mean of va minus mean of vb, both sets in one block bootstrap on their own times."""
    v = np.concatenate([va, vb]); t = np.concatenate([ta, tb])
    g = np.concatenate([np.ones(len(va), bool), np.zeros(len(vb), bool)])
    return group_diff(v, g, t)


def split_block(book, t, side, jts, d100=None):
    if d100 is None:
        d100 = dS_all(book, t, side)[:, J100]
    w = after_jump(t, jts)
    out = dict(group=readable(t, w), rest=readable(t, ~w), share_after_jump=float(w.mean()))
    out["dS100_after_jump_minus_rest"] = group_diff(d100, w, t)
    return out, w


def run_spec(book, name, spec, rt, rside, rd100, st, sside, sd100, rng_seed=JUMP_SEED):
    jts, jdir, jmv = jump_stamps(book, spec["k_bps"], spec["w_ms"])
    tj, dj, mj = spaced(book, jts, jdir, jmv)
    res = dict(spec=dict(spec, name=name), n_jump_stamps=int(len(jts)), n_spaced_jumps=int(len(tj)),
               share_spaced_up=float((dj > 0).mean()) if len(dj) else None)
    if len(tj):
        res["spaced_jump_size_bps_quantiles"] = {str(q): float(np.quantile(np.abs(mj), q)) for q in (0.5, 0.9, 0.99)}
    res["random"], wr = split_block(book, rt, rside, jts, rd100)
    res["signal"], _ = split_block(book, st, sside, jts, sd100)
    # jump decisions
    if len(tj):
        rng = np.random.default_rng(rng_seed)
        tdec = tj + rng.integers(0, WINDOW_MS * 1000 + 1, len(tj))
        jd = dict(readable(tdec, np.ones(len(tdec), bool)))
        rest_v = rd100[~wr]; rest_t = rt[~wr]
        for lab, sd in (("with_jump", dj), ("against_jump", -dj)):
            dS = dS_all(book, tdec, sd)
            allm = np.ones(len(tdec), bool)
            jd[lab] = dict(mean_dS100=group_mean(dS[:, J100], allm, tdec),
                           minus_random_rest=pooled_diff(dS[:, J100], tdec, rest_v, rest_t),
                           mean_dS_by_delay_ms={int(d): float(dS[:, j].mean()) for j, d in enumerate(DELAYS_MS)})
        res["jump_decisions"] = jd
        # stale top of book
        sc = dict(n=int(len(tj)))
        for h in STALE_H_MS:
            row = {}
            bg, bt = stale(book, rt, rside, h)
            row["baseline_random"] = dict(gone=group_mean(bg * 1.0, np.ones(len(rt), bool), rt),
                                          gone_or_below_size=group_mean(bt * 1.0, np.ones(len(rt), bool), rt))
            for lab, sd in (("with_jump", dj), ("against_jump", -dj)):
                g, th = stale(book, tj, sd, h)
                allm = np.ones(len(tj), bool)
                row[lab] = dict(gone=group_mean(g * 1.0, allm, tj),
                                gone_or_below_size=group_mean(th * 1.0, allm, tj),
                                gone_minus_baseline=pooled_diff(g * 1.0, tj, bg * 1.0, rt),
                                gone_or_below_minus_baseline=pooled_diff(th * 1.0, tj, bt * 1.0, rt))
            sc[f"{h}ms"] = row
        res["stale_top_of_book"] = sc
    return res


def results(day):
    book, _ = load_day(day)
    rt, rside, _ = make_decisions(book)
    st, sside, _, thr = make_signal_decisions(book, frozen_threshold())
    rd100 = dS_all(book, rt, rside)[:, J100]
    sd100 = dS_all(book, st, sside)[:, J100]
    res = dict(day=day, config=CONFIG, n_random=int(len(rt)), n_signal=int(len(st)), signal_threshold=thr,
               check_random_mean_dS100=float(rd100.mean()))
    res["specs"] = {name: run_spec(book, name, sp, rt, rside, rd100, st, sside, sd100) for name, sp in SPECS.items()}
    return res


def main(day):
    res = results(day)
    out = ROOT / "results" / "jump"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"jump_split_{day}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: (v["n_jump_stamps"], v["n_spaced_jumps"], v["random"]["group"]["n"],
                          v["signal"]["group"]["n"]) for k, v in res["specs"].items()}))


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    guard_day(day)
    main(day)
