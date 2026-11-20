"""Taker follow ups on the dev day, specified on 2026-11-19 before any of them was run.

  H1b interval   mean dS(100 ms) of decisions whose 1 s move went their way minus the rest
  H1b split B    exploratory. Same, with the groups set by the move from t + 100 ms to t + 1.1 s,
                 which shares no price change with dS(100 ms)
  RQ3            mean dS(100 ms) in the top fifth of realised volatility over the 10 s before t
                 minus the rest (H3), and the same split by |I| at t
  walk           the registered five level walk next to the top of book fill
  tie flip       decisions moved onto the whole millisecond grid, and the signal decisions, under
                 both tie rules
Decision sets are the random decisions, the same decisions floored to the whole millisecond
(exploratory), and the signal decisions (secondary).
Writes results/taker/followups_dev_<day>.json.
"""
import json
import os
import sys
import numpy as np

from .paths import ROOT
from .replay import book_index_at
from .passive import prep_day
from .taker import DELAYS_MS, QTY, make_decisions, slope_blocks, mean_ci
from .signals import make_signal_decisions, imbalance, frozen_threshold
from .stats import group_diff, group_mean

J100 = list(DELAYS_MS).index(100)
RV_WINDOW_US = 10 * 10**6
RV_STEP_US = 100 * 1000
TOP_FIFTH = 0.8


def mid_vec(book, tt, tie_after=True):
    k = book_index_at(book, tt, tie_after)
    k = np.maximum(k, 0)
    return 0.5 * (book.bid_px[k] + book.ask_px[k])


def realised_vol_bps(book, t):
    """Mid sampled every 100 ms over [t - 10 s, t] (last ticker row at or before each time),
    square root of the sum of squared log changes, in bps."""
    grid = t[:, None] - RV_WINDOW_US + RV_STEP_US * np.arange(RV_WINDOW_US // RV_STEP_US + 1)[None, :]
    m = mid_vec(book, grid.ravel()).reshape(grid.shape)
    r = np.diff(np.log(m), axis=1)
    return np.sqrt((r ** 2).sum(1)) * 1e4


def walk_px(book, S, ta, side, tie_after=True, qty=QTY):
    """Fill a marketable order of qty at arrival. Ticker touch first, then the five level snapshot
    levels strictly worse than the touch. Returns VWAP and a flag where five levels were not enough
    (the rest is priced at the last level used)."""
    k = np.maximum(book_index_at(book, ta, tie_after), 0)
    n = len(ta)
    px0 = np.where(side > 0, book.ask_px[k], book.bid_px[k])
    q0 = np.where(side > 0, book.ask_qty[k], book.bid_qty[k]).astype(float)
    take = np.minimum(qty, q0)
    rem = qty - take
    notional = take * px0
    last = px0.copy()
    for sd in (1, -1):
        sel = np.where(side == sd)[0]
        if len(sel) == 0:
            continue
        opp = S[-sd]                               # a buy walks the asks
        ks = np.searchsorted(opp["snap_ts"], ta[sel], "right" if tie_after else "left") - 1
        ok = ks >= 0
        lv_px = opp["snap_px"][np.maximum(ks, 0)] * (-sd)   # back to real prices
        lv_q = opp["snap_q"][np.maximum(ks, 0)]
        for L in range(5):
            p = lv_px[:, L]; q = lv_q[:, L]
            worse = (p > px0[sel]) if sd > 0 else (p < px0[sel])
            use = ok & worse & (rem[sel] > 1e-12)
            f = np.where(use, np.minimum(rem[sel], q), 0.0)
            notional[sel] += f * p
            rem[sel] -= f
            last[sel] = np.where(f > 0, p, last[sel])
    flag = rem > 1e-12
    notional += np.where(flag, rem * last, 0.0)
    return notional / qty, flag


def taker_arrays(book, S, t, side, tie_after=True, qty=QTY):
    n, nd = len(t), len(DELAYS_MS)
    mid0 = mid_vec(book, t, True)
    S_top = np.zeros((n, nd)); S_walk = np.zeros((n, nd)); flag_top = np.zeros((n, nd), bool)
    flag_walk = np.zeros((n, nd), bool)
    for j, dms in enumerate(DELAYS_MS):
        ta = t + int(dms) * 1000
        k = np.maximum(book_index_at(book, ta, tie_after), 0)
        px = np.where(side > 0, book.ask_px[k], book.bid_px[k])
        av = np.where(side > 0, book.ask_qty[k], book.bid_qty[k])
        S_top[:, j] = side * (px - mid0) / mid0 * 1e4
        flag_top[:, j] = av < qty
        wp, fl = walk_px(book, S, ta, side, tie_after, qty)
        S_walk[:, j] = side * (wp - mid0) / mid0 * 1e4
        flag_walk[:, j] = fl
    return dict(mid0=mid0, S=S_top, dS=S_top - S_top[:, [0]], S_walk=S_walk,
                dS_walk=S_walk - S_walk[:, [0]], flag_top=flag_top, flag_walk=flag_walk)


def h1_block(a, t, key="dS"):
    beta, ci = slope_blocks(a[key], t)
    m5, c5 = mean_ci(a[key][:, -1], t)
    m1, c1 = mean_ci(a[key][:, J100], t)
    return dict(slope_bps_per_logms=dict(est=beta, ci95=ci), mean_dS_100ms=dict(mean=m1, ci95=c1),
                mean_dS_500ms=dict(mean=m5, ci95=c5))


def analyse(book, S, t, side, tie_after=True):
    a = taker_arrays(book, S, t, side, tie_after)
    out = dict(n_decisions=int(len(t)), share_buys=float((side > 0).mean()))
    out["H1_top_of_book"] = h1_block(a, t, "dS")
    out["H1_five_level_walk"] = h1_block(a, t, "dS_walk")
    out["flag_share_top_by_delay_ms"] = {int(d): float(a["flag_top"][:, j].mean()) for j, d in enumerate(DELAYS_MS)}
    out["flag_share_walk_by_delay_ms"] = {int(d): float(a["flag_walk"][:, j].mean()) for j, d in enumerate(DELAYS_MS)}
    out["mean_S_by_delay_ms"] = {int(d): float(a["S"][:, j].mean()) for j, d in enumerate(DELAYS_MS)}
    d100 = a["dS"][:, J100]
    m1s = mid_vec(book, t + 10**6)
    pos = side * (m1s - a["mid0"]) > 0
    out["H1b_registered"] = group_diff(d100, pos, t)
    out["H1b_registered"]["share_group"] = float(pos.mean())
    mb = mid_vec(book, t + 100 * 1000); me = mid_vec(book, t + 1100 * 1000)
    pos2 = side * (me - mb) > 0
    out["H1b_split_B_exploratory"] = group_diff(d100, pos2, t)
    out["H1b_split_B_exploratory"]["share_group"] = float(pos2.mean())
    rv = realised_vol_bps(book, t)
    k0 = np.maximum(book_index_at(book, t, True), 0)
    absI = np.abs(imbalance(book.bid_qty[k0], book.ask_qty[k0]))
    for name, x in (("volatility", rv), ("abs_imbalance", absI)):
        cut = float(np.quantile(x, TOP_FIFTH))
        hi = x >= cut
        blk = dict(cut=cut, share_high=float(hi.mean()), dS100_high_minus_rest=group_diff(d100, hi, t),
                   by_delay={int(d): dict(high=group_mean(a["dS"][:, j], hi, t)["mean"],
                                          rest=group_mean(a["dS"][:, j], ~hi, t)["mean"])
                             for j, d in enumerate(DELAYS_MS)})
        out["RQ3_" + name] = blk
    out["RQ3_volatility"]["rv_bps_quantiles"] = {str(q): float(np.quantile(rv, q)) for q in (0.1, 0.5, 0.8, 0.9, 0.99)}
    s = np.sort(d100)[::-1]
    top = s[: max(1, int(0.1 * len(s)))]
    out["tail_share_worst10pct_dS100"] = float(top.sum() / d100.sum()) if d100.sum() != 0 else None
    out["dS100_sum_bps"] = float(d100.sum())
    return out, a


def tie_compare(book, S, t, side):
    ra, aa = analyse(book, S, t, side, True)
    rb, ab = analyse(book, S, t, side, False)
    changed = (aa["S"] != ab["S"])
    return dict(tie_after=ra["H1_top_of_book"], tie_before=rb["H1_top_of_book"],
                tie_after_walk=ra["H1_five_level_walk"], tie_before_walk=rb["H1_five_level_walk"],
                share_cells_changed=float(changed.mean()),
                share_cells_changed_by_delay_ms={int(d): float(changed[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
                mean_S_before_minus_after_by_delay_ms={int(d): float((ab["S"][:, j] - aa["S"][:, j]).mean()) for j, d in enumerate(DELAYS_MS)})


def signal_decisions(book):
    """Signal decisions at the frozen dev day threshold, on any day."""
    return make_signal_decisions(book, frozen_threshold())


def main(day):
    book, tr, S = prep_day(day)
    t, side, ngaps = make_decisions(book)
    ts, ss, ngs, thr = signal_decisions(book)
    res = dict(day=day)
    res["random"], _ = analyse(book, S, t, side, True)
    res["signal"], _ = analyse(book, S, ts, ss, True)
    res["signal"]["threshold_abs_imbalance"] = thr
    res["tie_flip_random_us_decisions"] = tie_compare(book, S, t, side)
    tg = t - t % 1000
    res["tie_flip_random_ms_grid_exploratory"] = tie_compare(book, S, tg, side)
    res["tie_flip_signal"] = tie_compare(book, S, ts, ss)
    out = ROOT / "results" / "taker"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"followups_dev_{day}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k]["n_decisions"] for k in ("random", "signal")}))


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    if day != "2026-09-01" and os.environ.get("S2F_ALLOW_TEST_DAY") != "1":
        sys.exit("dev day only until the test day run is started on purpose")
    main(day)
