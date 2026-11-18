"""Fixed price passive arm (H5), preregistered under Deviations on 2026-11-18.

The limit price is the best price on my own side at decision time t and never changes.
At t + d the order is posted at that price.
  marketable  the book has moved through my price, so the part that can trade fills against the
              arrival touch as a taker (top of book only, as in the taker leg), and the rest rests at
              my price with nothing ahead of it
  joins       the best on my side is still my price, so I join behind the displayed size
  inside      the best on my side moved toward the other side but my price is not marketable, so
              I am alone at a price better than the book's best, nothing ahead
  behind      the best on my side moved away, so I sit at my price behind the new best. Queue ahead
              is the displayed size at my price in the last five level snapshot at or before arrival.
              If my price is below the top five at arrival, the order counts as unfilled from the start
Queue rules, horizon (10 s from arrival), markouts and post then cross cost follow passive.py.
Everything is in buy like terms (sell prices multiplied by minus one), as in passive.py.
"""
import json
import os
import sys
import numpy as np

from .paths import ROOT
from .replay import book_index_at
from .passive import walk, prep_day, QTY, H_US, RULES
from .taker import DELAYS_MS, SEED, BLOCK_US, make_decisions, slope_blocks, mean_ci

STATES = ("marketable", "joins", "inside", "behind", "below_top_five")


def arrival_state(p, my_best, my_qty, opp_best, opp_qty, snap_px, snap_q, qty=QTY):
    """Where a fixed price order stands when it reaches the book. All prices buy like.
    Returns (state, taker_qty, ahead, best_above)."""
    if p >= opp_best:
        return "marketable", float(min(qty, opp_qty)), 0.0, False
    if my_best == p:
        return "joins", 0.0, float(my_qty), False
    if my_best < p:
        return "inside", 0.0, 0.0, False
    hit = np.where(snap_px == p)[0]
    if len(hit):
        return "behind", 0.0, float(snap_q[hit[0]]), True
    if p < snap_px.min():
        return "below_top_five", 0.0, 0.0, True
    return "behind", 0.0, 0.0, True               # a gap in the snapshot at my price


def one_fixed(book, S, t, side, d_us, rule_rng_seed, tie_after=True):
    s = S[side]
    k0 = book_index_at(book, t, True)
    ta = t + d_us
    k = book_index_at(book, ta, tie_after)
    if k0 < 0 or k < 0:
        return None
    p = (book.bid_px[k0] if side > 0 else book.ask_px[k0]) * side
    my_best = (book.bid_px[k] if side > 0 else book.ask_px[k]) * side
    my_q = float(book.bid_qty[k] if side > 0 else book.ask_qty[k])
    opp_real = book.ask_px[k] if side > 0 else book.bid_px[k]
    opp_best = opp_real * side
    opp_q = float(book.ask_qty[k] if side > 0 else book.bid_qty[k])
    ks = np.searchsorted(s["snap_ts"], ta, "right") - 1
    spx = s["snap_px"][ks] if ks >= 0 else np.full(5, np.inf)
    sq = s["snap_q"][ks] if ks >= 0 else np.zeros(5)
    state, tq, ahead, above = arrival_state(p, my_best, my_q, opp_best, opp_q, spx, sq)
    filled_t = np.full(3, tq)
    filled_r = np.zeros(3)
    fill_t = np.full(3, -1, dtype=np.int64)
    lost = state == "below_top_five"
    if tq >= QTY - 1e-12:
        fill_t[:] = ta
    elif not lost:
        tend = ta + H_US
        lo_t = np.searchsorted(s["tr_ts"], ta, "right"); hi_t = np.searchsorted(s["tr_ts"], tend, "right")
        lo_k = np.searchsorted(s["tick_ts"], ta, "right"); hi_k = np.searchsorted(s["tick_ts"], tend, "right")
        lo_s = np.searchsorted(s["snap_ts"], ta, "right"); hi_s = np.searchsorted(s["snap_ts"], tend, "right")
        nt, nk, ns = hi_t - lo_t, hi_k - lo_k, hi_s - lo_s
        ts = np.concatenate([s["tr_ts"][lo_t:hi_t], s["tick_ts"][lo_k:hi_k], s["snap_ts"][lo_s:hi_s]])
        kind = np.concatenate([np.zeros(nt, int), np.ones(nk, int), np.full(ns, 2)])
        a = np.concatenate([s["tr_px"][lo_t:hi_t], s["tick_px"][lo_k:hi_k], np.zeros(ns)])
        b = np.concatenate([s["tr_q"][lo_t:hi_t], s["tick_q"][lo_k:hi_k], np.zeros(ns)])
        epx = np.zeros((len(ts), 5)); eq = np.zeros((len(ts), 5))
        epx[nt + nk:] = s["snap_px"][lo_s:hi_s]; eq[nt + nk:] = s["snap_q"][lo_s:hi_s]
        o = np.lexsort((kind, ts))
        rng = np.random.default_rng(rule_rng_seed)
        rest = QTY - tq
        fr, fev, lost_ev = walk(p, ahead, kind[o], a[o], b[o], epx[o], eq[o], rng, qty=rest, best_above0=above)
        filled_r = fr
        lost = lost_ev >= 0
        ts_o = ts[o]
        fill_t = np.where(fev >= 0, ts_o[np.maximum(fev, 0)] if len(ts_o) else -1, -1)
    p_real = p * side
    tot = filled_t + filled_r
    vwap = np.where(tot > 0, (filled_t * opp_real + filled_r * p_real) / np.maximum(tot, 1e-18), np.nan)
    return dict(state=state, filled=tot, vwap=vwap, fill_t=fill_t, lost=bool(lost), ta=ta)


def run(day="2026-09-01", lo=0, hi=None, tie_after=True):
    book, tr, S = prep_day(day)
    t, side, ngaps = make_decisions(book)
    hi = len(t) if hi is None else min(hi, len(t))
    idx = np.arange(lo, hi)
    n, nd = len(idx), len(DELAYS_MS)
    fill = np.zeros((n, nd, 3)); frac = np.zeros((n, nd, 3))
    cost = np.full((n, nd, 3), np.nan); m10 = np.full((n, nd, 3), np.nan)
    state = np.zeros((n, nd), int); lost = np.zeros((n, nd), bool); valid = np.ones(n, bool)

    def mid(tt):
        kk = book_index_at(book, tt, True)
        return 0.5 * (book.bid_px[kk] + book.ask_px[kk])

    for ii, i in enumerate(idx):
        mid0 = mid(t[i])
        for j, dms in enumerate(DELAYS_MS):
            r = one_fixed(book, S, t[i], side[i], int(dms) * 1000, (SEED, int(i), j), tie_after)
            if r is None:
                valid[ii] = False
                continue
            state[ii, j] = STATES.index(r["state"]); lost[ii, j] = r["lost"]
            kx = book_index_at(book, r["ta"] + H_US, True)
            cross = book.ask_px[kx] if side[i] > 0 else book.bid_px[kx]
            c_x = side[i] * (cross - mid0) / mid0 * 1e4
            for q in range(3):
                f = r["filled"][q] / QTY
                frac[ii, j, q] = f
                full = f >= 1 - 1e-9
                fill[ii, j, q] = float(full)
                c_m = side[i] * (r["vwap"][q] - mid0) / mid0 * 1e4 if f > 0 else 0.0
                cost[ii, j, q] = f * c_m + (1 - f) * c_x
                if full:
                    tf = r["fill_t"][q]
                    m10[ii, j, q] = side[i] * (mid(tf + 10 * 10**6) - r["vwap"][q]) / r["vwap"][q] * 1e4
    v = valid
    return dict(i=idx[v], t=t[idx][v], side=side[idx][v], fill=fill[v], frac=frac[v], cost=cost[v],
                m10=m10[v], state=state[v], lost=lost[v], ngaps=np.array(ngaps))


def pooled_slope(Y, t, nboot=2000, seed=SEED):
    """Slope of Y on log(d) pooled over every finite (decision, delay) cell, 5 minute block bootstrap.
    Used for markouts, which exist only where the order filled."""
    x = np.log(DELAYS_MS.astype(float))
    X = np.broadcast_to(x, Y.shape)
    m = np.isfinite(Y)
    Yz = np.where(m, Y, 0.0); Xz = np.where(m, X, 0.0)
    blk = ((t - t.min()) // BLOCK_US).astype(int)
    ub, inv = np.unique(blk, return_inverse=True)
    sums = [np.bincount(inv, a.sum(1), minlength=len(ub)) for a in (m * 1.0, Xz, Yz, Xz * Yz, Xz * Xz)]
    sums = np.array(sums)                                   # 5 x blocks

    def slope(tot):
        n, sx, sy, sxy, sxx = tot
        return (sxy - sx * sy / n) / (sxx - sx * sx / n)
    est = slope(sums.sum(1))
    rng = np.random.default_rng(seed)
    bi = rng.integers(0, len(ub), (nboot, len(ub)))
    boots = slope(sums[:, bi].sum(2))
    return float(est), [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]


def summarize(r):
    t = r["t"]
    out = dict(n_decisions=int(len(t)), feed_gaps_over_1s=int(r["ngaps"]),
               arrival_state_share_by_delay={int(d): {nm: float((r["state"][:, j] == k).mean()) for k, nm in enumerate(STATES)}
                                             for j, d in enumerate(DELAYS_MS)},
               share_left_top_five_by_delay={int(d): float(r["lost"][:, j].mean()) for j, d in enumerate(DELAYS_MS)},
               by_rule={})
    for q, name in enumerate(RULES):
        F = r["fill"][:, :, q]; C = r["cost"][:, :, q]; M = r["m10"][:, :, q]
        fb, fci = slope_blocks(F, t)
        cb, cci = slope_blocks(C, t)
        mb, mci = pooled_slope(M, t)
        o = dict(fill_prob_by_delay={int(d): float(F[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
                 partial_share_by_delay={int(d): float(((r["frac"][:, j, q] > 0) & (F[:, j] == 0)).mean()) for j, d in enumerate(DELAYS_MS)},
                 fill_slope_per_logms=dict(est=fb, ci95=fci),
                 post_then_cross_cost_by_delay={int(d): float(C[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
                 H5_post_then_cross_cost_slope_bps_per_logms=dict(est=cb, ci95=cci),
                 markout_10s_by_delay={int(d): dict(mean=float(np.nanmean(M[:, j])) if np.isfinite(M[:, j]).any() else None,
                                                    n=int(np.isfinite(M[:, j]).sum())) for j, d in enumerate(DELAYS_MS)},
                 markout_10s_slope_bps_per_logms=dict(est=mb, ci95=mci))
        o["post_then_cross_cost_by_arrival_state"] = {
            int(d): {nm: dict(n=int((r["state"][:, j] == k).sum()),
                              mean=float(C[r["state"][:, j] == k, j].mean()) if (r["state"][:, j] == k).any() else None)
                     for k, nm in enumerate(STATES)} for j, d in enumerate(DELAYS_MS)}
        o["cost_500ms_minus_1ms"] = dict(zip(("mean", "ci95"), mean_ci(C[:, -1] - C[:, 0], t)))
        o["fill_drop_1ms_to_500ms"] = dict(zip(("mean", "ci95"), mean_ci(F[:, 0] - F[:, -1], t)))
        out["by_rule"][name] = o
    return out


def save_chunk(day, lo, hi, path):
    r = run(day, lo, hi)
    np.savez(path, **r)


def load_chunks(paths):
    parts = [dict(np.load(p)) for p in sorted(paths, key=lambda p: int(np.load(p)["i"][0]))]
    r = {k: np.concatenate([p[k] for p in parts]) for k in parts[0] if k != "ngaps"}
    r["ngaps"] = parts[0]["ngaps"]
    assert (np.diff(r["i"]) > 0).all()
    return r


def write(day, res):
    outp = ROOT / "results" / "passive"
    outp.mkdir(parents=True, exist_ok=True)
    (outp / f"fixed_price_dev_{day}.json").write_text(json.dumps({"random_decisions": res}, indent=1))


if __name__ == "__main__":
    # python -m s2f.fixed_price DAY                 full run, writes the results file
    # python -m s2f.fixed_price DAY chunk LO HI F   one slice of decisions to an npz file
    # python -m s2f.fixed_price DAY merge F1 F2 ... merge slices and write the results file
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    if day != "2026-09-01" and os.environ.get("S2F_ALLOW_TEST_DAY") != "1":
        sys.exit("fixed price arm runs on the dev day only until the test day run is started on purpose")
    mode = sys.argv[2] if len(sys.argv) > 2 else "full"
    if mode == "chunk":
        save_chunk(day, int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif mode == "merge":
        res = summarize(load_chunks(sys.argv[3:]))
        write(day, res)
        print(json.dumps({k: v["H5_post_then_cross_cost_slope_bps_per_logms"] for k, v in res["by_rule"].items()}, indent=1))
    else:
        res = summarize(run(day))
        write(day, res)
        print(json.dumps({k: v["H5_post_then_cross_cost_slope_bps_per_logms"] for k, v in res["by_rule"].items()}, indent=1))
