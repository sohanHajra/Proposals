"""C1, C2 and the secondary checks for one day, built from the 01 functions at tag v0.1-signal-to-fill.

C1   signal decisions at the stored threshold. Slope of the five level walk dS(d) on log d and the
     mean walk dS(500 ms), 5 minute block bootstrap, 2,000 resamples, seed 20261115.
     Also the drift and arrival split of dS(500 ms) and the race sensitivity (Deviation of
     2026-11-23, items 7 and 8), the tie flip, fees, 15 minute blocks and the placebo.
C2   random decisions, fixed price passive (s2f.fixed_price.run), every decision marketable on arrival
     at any delay left out (s2f.passive_followups.drop_marketable), slope of the post then cross cost
     on log d under each cancellation rule. Then the tie flip, fees, 15 minute blocks and the placebo.

Nothing here is tuned to a day. Every number is fixed in the preregistration or its Deviations.
"""
from contextlib import contextmanager

import numpy as np

from . import paths  # noqa: F401
from s2f import fixed_price, passive
from s2f.taker import DELAYS_MS, SEED, slope_blocks, mean_ci, shuffle_rows, make_decisions
from s2f.taker_followups import taker_arrays, walk_px, mid_vec
from s2f.signals import make_signal_decisions
from s2f.passive import RULES
from s2f.fixed_price import STATES
from s2f.robustness import FEES, BLOCK15_US

J1, J500 = 0, len(DELAYS_MS) - 1
RACE_US = 1000
C1_MIN_MEAN_500 = 0.1


def by_delay(M):
    return {int(d): float(np.nanmean(M[:, j])) for j, d in enumerate(DELAYS_MS)}


def line(dS, t, block_us=None):
    kw = {} if block_us is None else dict(block_us=block_us)
    b, ci = slope_blocks(dS, t, **kw)
    m, mci = mean_ci(dS[:, J500], t, **kw)
    return dict(slope_bps_per_logms=dict(est=b, ci95=ci), mean_dS_500ms=dict(mean=m, ci95=mci))


def race_arrays(book, S, t, side, qty, race_us=RACE_US):
    """Walk shortfall under the race rule (Deviation of 2026-11-23, item 7). Primary tie rule."""
    n, nd = len(t), len(DELAYS_MS)
    mid0 = mid_vec(book, t, True)
    Sr = np.zeros((n, nd)); kept = np.zeros((n, nd), bool); changed = np.zeros((n, nd), bool)
    worse = np.zeros((n, nd), bool); better = np.zeros((n, nd), bool)
    for j, dms in enumerate(DELAYS_MS):
        ta = t + int(dms) * 1000
        k0 = np.maximum(book.ts.searchsorted(ta, "right") - 1, 0)
        k1 = np.maximum(book.ts.searchsorted(ta + race_us, "right") - 1, 0)
        p0 = np.where(side > 0, book.ask_px[k0], book.bid_px[k0])
        p1 = np.where(side > 0, book.ask_px[k1], book.bid_px[k1])
        q1 = np.where(side > 0, book.ask_qty[k1], book.bid_qty[k1])
        keep = (p1 == p0) & (q1 >= qty)
        wa, _ = walk_px(book, S, ta, side, True, qty)
        wb, _ = walk_px(book, S, ta + race_us, side, True, qty)
        w = np.where(keep, wa, wb)
        Sr[:, j] = side * (w - mid0) / mid0 * 1e4
        kept[:, j] = keep
        changed[:, j] = w != wa
        worse[:, j] = side * (w - wa) > 0
        better[:, j] = side * (w - wa) < 0
    return dict(S=Sr, dS=Sr - Sr[:, [0]], kept=kept, changed=changed, worse=worse, better=better)


def c1(book, S, t, side, qty):
    a = taker_arrays(book, S, t, side, True, qty)
    out = dict(n_decisions=int(len(t)), share_buys=float((side > 0).mean()) if len(t) else None, order_size=qty)
    out["walk"] = line(a["dS_walk"], t)
    out["walk"]["mean_S_by_delay_ms"] = by_delay(a["S_walk"])
    out["walk"]["flag_share_beyond_five_levels_by_delay_ms"] = by_delay(a["flag_walk"].astype(float))
    out["top_of_book"] = line(a["dS"], t)
    # drift and arrival split of dS(500 ms), primary tie rule
    mid0 = a["mid0"]
    dr = np.zeros_like(a["S_walk"])
    for j, dms in enumerate(DELAYS_MS):
        dr[:, j] = side * (mid_vec(book, t + int(dms) * 1000, True) - mid0) / mid0 * 1e4
    ar = a["S_walk"] - dr
    md, mdci = mean_ci(dr[:, J500] - dr[:, J1], t)
    ma, maci = mean_ci(ar[:, J500] - ar[:, J1], t)
    out["split_dS_500ms"] = dict(drift=dict(mean=md, ci95=mdci), arrival=dict(mean=ma, ci95=maci),
                                 drift_by_delay_ms=by_delay(dr), arrival_by_delay_ms=by_delay(ar))
    # race sensitivity
    r = race_arrays(book, S, t, side, qty)
    out["race"] = line(r["dS"], t)
    out["race"]["mean_S_by_delay_ms"] = by_delay(r["S"])
    out["race"]["share_cells_changed"] = float(r["changed"].mean())
    out["race"]["share_cells_worse"] = float(r["worse"].mean())
    out["race"]["share_cells_better"] = float(r["better"].mean())
    out["race"]["share_changed_by_delay_ms"] = by_delay(r["changed"].astype(float))
    # secondary
    b = taker_arrays(book, S, t, side, False, qty)
    out["tie_before"] = line(b["dS_walk"], t)
    out["tie_before"]["share_cells_changed"] = float((b["S_walk"] != a["S_walk"]).mean())
    Sf = a["S_walk"] + FEES["taker_bps"]
    out["fees"] = line(Sf - Sf[:, [0]], t)
    out["fees"]["mean_S_500ms_with_fees"] = float(Sf[:, J500].mean())
    out["fees"]["fees"] = FEES
    out["blocks15"] = line(a["dS_walk"], t, BLOCK15_US)
    pl = shuffle_rows(a["dS_walk"])
    out["placebo"] = line(pl, t)
    out["placebo"]["shuffle_seed"] = SEED + 1
    out["placebo"]["interval_covers_zero"] = bool(out["placebo"]["slope_bps_per_logms"]["ci95"][0] <= 0 <= out["placebo"]["slope_bps_per_logms"]["ci95"][1])
    ci = out["walk"]["slope_bps_per_logms"]["ci95"]
    out["day_counts"] = dict(slope_interval_above_zero=bool(ci[0] > 0), slope_interval_below_zero=bool(ci[1] < 0),
                             mean_dS_500ms_at_least_0_1=bool(out["walk"]["mean_dS_500ms"]["mean"] >= C1_MIN_MEAN_500))
    return out


def signal_decisions(book, thr):
    t, side, ngaps, thr = make_signal_decisions(book, thr)
    return t, side, ngaps


@contextmanager
def order_size(qty):
    """fixed_price reads its size from the module constant QTY and from the default of arrival_state.
    For ETHUSDT both are set to the ETHUSDT size for the length of the run, then put back."""
    q0, d0 = fixed_price.QTY, fixed_price.arrival_state.__defaults__
    fixed_price.QTY = qty
    fixed_price.arrival_state.__defaults__ = (qty,)
    try:
        yield
    finally:
        fixed_price.QTY = q0
        fixed_price.arrival_state.__defaults__ = d0


def c2_replay(prepped, tie_after, qty):
    book = prepped[0]
    dec = make_decisions(book)
    with order_size(qty):
        r = fixed_price.run("", tie_after=tie_after, decisions=dec, prepped=prepped)
    r.pop("i", None)
    r["ngaps"] = np.array(r["ngaps"])
    return r


def keep_mask(r):
    return ~(r["state"] == STATES.index("marketable")).any(1)


def c2_lines(r, block_us=None, fees=False, placebo=False):
    keep = keep_mask(r); t = r["t"][keep]
    out = dict(n_decisions=int(len(r["t"])), n_dropped=int((~keep).sum()), n_kept=int(keep.sum()))
    kw = {} if block_us is None else dict(block_us=block_us)
    for q, nm in enumerate(RULES):
        C = r["cost"][keep][:, :, q]
        if fees:
            f = r["frac"][keep][:, :, q]
            C = C + f * FEES["maker_bps"] + (1 - f) * FEES["taker_bps"]
        if placebo:
            C = shuffle_rows(C)
        b, ci = slope_blocks(C, t, **kw)
        out[nm] = dict(slope_bps_per_logms=dict(est=b, ci95=ci), cost_by_delay=by_delay(C))
    return out


def c2(r_after, r_before=None):
    from s2f.passive_followups import drop_marketable
    out = dict(primary=drop_marketable(r_after))
    mine = c2_lines(r_after)
    out["primary_check_same_as_01_function"] = all(
        mine[nm]["slope_bps_per_logms"] == out["primary"][nm]["slope_bps_per_logms"] for nm in RULES)
    out["day_counts"] = {nm: dict(slope_interval_above_zero=bool(out["primary"][nm]["slope_bps_per_logms"]["ci95"][0] > 0),
                                  slope_interval_below_zero=bool(out["primary"][nm]["slope_bps_per_logms"]["ci95"][1] < 0))
                         for nm in RULES}
    out["fees"] = c2_lines(r_after, fees=True); out["fees"]["fees"] = FEES
    out["blocks15"] = c2_lines(r_after, block_us=BLOCK15_US)
    out["placebo"] = c2_lines(r_after, placebo=True); out["placebo"]["shuffle_seed"] = SEED + 1
    out["placebo"]["interval_covers_zero"] = {nm: bool(out["placebo"][nm]["slope_bps_per_logms"]["ci95"][0] <= 0 <= out["placebo"][nm]["slope_bps_per_logms"]["ci95"][1]) for nm in RULES}
    if r_before is not None:
        out["tie_before"] = drop_marketable(r_before)
    return out
