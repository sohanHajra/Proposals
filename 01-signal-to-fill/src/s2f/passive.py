"""Passive leg on the dev day. A 0.01 BTC limit order joins the best price on its own side at t + d.

Everything is written in "buy like" terms. For a sell, prices are multiplied by minus one, so a higher
number is always a better price for my side. The queue marker is virtual and never changes the book.
Inside one timestamp the order is trades, then book updates (ticker, then snapshot).
Three cancellation rules run on the same path, seeds and trades.
  front  cancels remove the oldest quantity first
  random a cancel is one lump placed uniformly inside the queue (seeded)
  back   cancels remove the newest quantity first
"""
import json
import sys
import numpy as np
import polars as pl

from .paths import ROOT, RAW, result_path, guard_day, float_prices
from .replay import load_day, book_index_at, CLOCKS
from .taker import DELAYS_MS, SEED, make_decisions, slope_blocks, mean_ci

QTY = 0.01
H_US = 10 * 10**6
RULES = ("front", "random", "back")
T_TRADE, T_TICK, T_SNAP = 0, 1, 2


def walk(p, ahead0, ev_kind, ev_a, ev_b, ev_snap_px, ev_snap_q, rng, qty=QTY, best_above0=False):
    """Walk the queue marker through ordered events, all three rules at once.
    Events by kind.
      trade  a = opposing trade price (buy like), b = size
      tick   a = my side best price (buy like), b = displayed size there
      snap   ev_snap_px, ev_snap_q = my side top five prices (buy like) and sizes
    Returns filled amount per rule (array of 3) and the index of the event where the marker
    left the top five (or -1). Time of the fill is returned per rule as event index (or -1)."""
    A = np.array([ahead0, ahead0, ahead0], float)
    Bq = np.zeros(3)
    filled = np.zeros(3)
    fill_ev = np.full(3, -1)
    lost = -1
    best_above = best_above0   # a better price than mine is on the book (last tick)
    for e in range(len(ev_kind)):
        k = ev_kind[e]
        if k == T_TRADE:
            px, q = ev_a[e], ev_b[e]
            if px > p:
                continue
            for r in range(3):
                if filled[r] >= qty:
                    continue
                if px < p:                       # trade through my price, I am done
                    filled[r] = qty; fill_ev[r] = e; continue
                take = min(A[r], q)
                A[r] -= take
                rest = q - take
                if rest > 0:
                    f = min(rest, qty - filled[r])
                    filled[r] += f
                    if filled[r] >= qty - 1e-12:
                        filled[r] = qty; fill_ev[r] = e
                    else:
                        pass
                    # whatever is left of rest would reduce the queue behind me, which I do not track
            if (filled >= qty).all():
                break
            continue
        # book updates
        if k == T_TICK:
            px, q = ev_a[e], ev_b[e]
            if px > p:
                best_above = True
                continue
            best_above = False
            qobs = q if px == p else 0.0
        else:
            if not best_above:
                continue                           # the ticker already sees my level
            pxs = ev_snap_px[e]
            hit = np.where(pxs == p)[0]
            if len(hit) == 0:
                if p < pxs.min():                  # left the top five
                    lost = e
                    break
                qobs = 0.0
            else:
                qobs = ev_snap_q[e][hit[0]]
        for r in range(3):
            if filled[r] >= qty:
                continue
            Q = A[r] + Bq[r]
            d = qobs - Q
            if d > 0:
                Bq[r] += d
            elif d < 0:
                c = min(-d, Q)
                if r == 0:
                    a_cut = min(A[r], c)
                elif r == 2:
                    a_cut = max(0.0, c - Bq[r])
                else:
                    if c >= Q:
                        a_cut = A[r]
                    else:
                        x = rng.random() * (Q - c)
                        a_cut = max(0.0, min(A[r], x + c) - x)
                A[r] -= a_cut
                Bq[r] = max(0.0, Bq[r] - (c - a_cut))
    return filled, fill_ev, lost


def prep_day(day, clock="exchange"):
    """clock="local" puts every file on local capture time (robustness 3)."""
    book, tr = load_day(day, clock=clock)
    col = CLOCKS[clock]
    fs = RAW / "tardis" / f"binance-futures_book_snapshot_5_{day}_BTCUSDT.csv.gz"
    snap = pl.read_csv(fs, schema_overrides=float_prices(fs))
    snap = snap.sort(col, maintain_order=True)
    sts = snap[col].to_numpy()
    sd = {}
    for side in (1, -1):
        name = "bids" if side > 0 else "asks"
        px = np.column_stack([snap[f"{name}[{i}].price"].to_numpy() for i in range(5)]) * side
        q = np.column_stack([snap[f"{name}[{i}].amount"].to_numpy() for i in range(5)])
        sd[side] = (px, q)
    S = {}
    for side in (1, -1):
        tp = (book.bid_px if side > 0 else book.ask_px) * side
        tq = (book.bid_qty if side > 0 else book.ask_qty).astype(float)
        ch = np.ones(len(tp), bool)
        ch[1:] = (tp[1:] != tp[:-1]) | (tq[1:] != tq[:-1])      # keep rows where my side changed
        idx = np.where(ch)[0]
        opp = tr.side == -side                                   # buy order is hit by sellers
        S[side] = dict(tick_ts=book.ts[idx], tick_px=tp[idx], tick_q=tq[idx],
                       tr_ts=tr.ts[opp], tr_px=tr.px[opp] * side, tr_q=tr.qty[opp],
                       snap_ts=sts, snap_px=sd[side][0], snap_q=sd[side][1])
    return book, tr, S


def one(book, S, t, side, d_us, rule_rng_seed, tie_after=True, qty=QTY, h_us=H_US):
    """Run one decision at one delay. Returns dict or None when no book was seen yet.
    qty and h_us differ from 0.01 BTC and 10 s only in the robustness checks."""
    s = S[side]
    ta = t + d_us
    k = book_index_at(book, ta, tie_after)
    if k < 0:
        return None
    mid0 = None
    my_px = (book.bid_px[k] if side > 0 else book.ask_px[k]) * side
    q0 = float(book.bid_qty[k] if side > 0 else book.ask_qty[k])
    tend = ta + h_us
    # tie after: events stamped exactly ta are already in the book I see, so the walk starts after them.
    # tie before: I see the book strictly before ta and every event stamped ta is replayed after I arrive.
    lo_side = "right" if tie_after else "left"
    lo_t = np.searchsorted(s["tr_ts"], ta, lo_side); hi_t = np.searchsorted(s["tr_ts"], tend, "right")
    lo_k = np.searchsorted(s["tick_ts"], ta, lo_side); hi_k = np.searchsorted(s["tick_ts"], tend, "right")
    lo_s = np.searchsorted(s["snap_ts"], ta, lo_side); hi_s = np.searchsorted(s["snap_ts"], tend, "right")
    nt, nk, ns = hi_t - lo_t, hi_k - lo_k, hi_s - lo_s
    ts = np.concatenate([s["tr_ts"][lo_t:hi_t], s["tick_ts"][lo_k:hi_k], s["snap_ts"][lo_s:hi_s]])
    kind = np.concatenate([np.zeros(nt, int), np.ones(nk, int), np.full(ns, 2)])
    a = np.concatenate([s["tr_px"][lo_t:hi_t], s["tick_px"][lo_k:hi_k], np.zeros(ns)])
    b = np.concatenate([s["tr_q"][lo_t:hi_t], s["tick_q"][lo_k:hi_k], np.zeros(ns)])
    spx = np.zeros((len(ts), 5)); sq = np.zeros((len(ts), 5))
    spx[nt + nk:] = s["snap_px"][lo_s:hi_s]; sq[nt + nk:] = s["snap_q"][lo_s:hi_s]
    o = np.lexsort((kind, ts))
    rng = np.random.default_rng(rule_rng_seed)
    filled, fev, lost = walk(my_px, q0, kind[o], a[o], b[o], spx[o], sq[o], rng, qty=qty)
    return dict(p=my_px * side, filled=filled, fill_t=np.where(fev >= 0, ts[o][np.maximum(fev, 0)] if len(ts) else -1, -1),
                lost=lost >= 0, ta=ta)


def run(day="2026-09-01", tie_after=True, max_n=None, decisions=None, prepped=None,
        qty=QTY, h_us=H_US, cross_walk=False):
    """decisions=(t, side, ngaps) replaces the random decisions; prepped=(book, tr, S) skips loading.
    qty, h_us and cross_walk are for the robustness checks only. cross_walk prices the part that
    crosses at the horizon with the five level walk instead of the touch."""
    book, tr, S = prepped if prepped is not None else prep_day(day)
    t, side, ngaps = decisions if decisions is not None else make_decisions(book)
    if max_n:
        t, side = t[:max_n], side[:max_n]
    n, nd = len(t), len(DELAYS_MS)
    fill = np.zeros((n, nd, 3)); frac = np.zeros((n, nd, 3))
    cost = np.full((n, nd, 3), np.nan); m1 = np.full((n, nd, 3), np.nan); m10 = np.full((n, nd, 3), np.nan)
    lost = np.zeros((n, nd), bool); valid = np.ones(n, bool)
    xflag = np.zeros((n, nd, 3), bool)
    if cross_walk:
        from .taker_followups import walk_px
    mid = lambda tt: 0.5 * (book.bid_px[book_index_at(book, tt, True)] + book.ask_px[book_index_at(book, tt, True)])
    for i in range(n):
        mid0 = mid(t[i])
        for j, dms in enumerate(DELAYS_MS):
            r = one(book, S, t[i], side[i], int(dms) * 1000, (SEED, i, j), tie_after, qty, h_us)
            if r is None:
                valid[i] = False; continue
            lost[i, j] = r["lost"]
            kx = book_index_at(book, r["ta"] + h_us, True)
            cross = (book.ask_px[kx] if side[i] > 0 else book.bid_px[kx])
            for q in range(3):
                f = r["filled"][q] / qty
                frac[i, j, q] = f
                fill[i, j, q] = float(f >= 1 - 1e-9)
                c_m = side[i] * (r["p"] - mid0) / mid0 * 1e4
                cx = cross
                if cross_walk and f < 1 - 1e-9:
                    wp, fl = walk_px(book, S, np.array([r["ta"] + h_us]), np.array([side[i]]), True,
                                     qty * (1 - f))
                    cx = float(wp[0]); xflag[i, j, q] = bool(fl[0])
                c_x = side[i] * (cx - mid0) / mid0 * 1e4
                cost[i, j, q] = f * c_m + (1 - f) * c_x
                if fill[i, j, q]:
                    tf = r["fill_t"][q]
                    m1[i, j, q] = side[i] * (mid(tf + 10**6) - r["p"]) / r["p"] * 1e4
                    m10[i, j, q] = side[i] * (mid(tf + 10 * 10**6) - r["p"]) / r["p"] * 1e4
    v = valid
    out = dict(t=t[v], side=side[v], fill=fill[v], frac=frac[v], cost=cost[v], m1=m1[v], m10=m10[v],
               lost=lost[v], ngaps=ngaps)
    if cross_walk:
        out["cross_flag"] = xflag[v]
    return out


def summarize(r):
    t = r["t"]; out = dict(n_decisions=int(len(t)), feed_gaps_over_1s=int(r["ngaps"]), by_rule={})
    for q, name in enumerate(RULES):
        F = r["fill"][:, :, q]
        beta, ci = slope_blocks(F, t)       # slope of fill probability on log delay, 5 minute blocks
        bc, bci = slope_blocks(r["cost"][:, :, q], t)
        o = dict(fill_prob_by_delay={int(d): float(F[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
                 partial_share_by_delay={int(d): float(((r["frac"][:, j, q] > 0) & (F[:, j] == 0)).mean()) for j, d in enumerate(DELAYS_MS)},
                 H2_slope_fill_per_logms=dict(est=beta, ci95=ci),
                 post_then_cross_cost_slope_bps_per_logms=dict(est=bc, ci95=bci),
                 post_then_cross_cost_by_delay={int(d): float(np.nanmean(r["cost"][:, j, q])) for j, d in enumerate(DELAYS_MS)})
        d_fill = F[:, 0] - F[:, -1]
        o["drop_1ms_to_500ms"] = dict(zip(("mean", "ci95"), mean_ci(d_fill, t)))
        both = (F[:, 0] == 1) & (F[:, -1] == 1)
        mk = {}
        for h, arr in (("1s", r["m1"]), ("10s", r["m10"])):
            a1, a5 = arr[:, 0, q], arr[:, -1, q]
            mk[h] = dict(mean_filled_1ms=float(np.nanmean(a1)), mean_filled_500ms=float(np.nanmean(a5)),
                         n_filled_1ms=int((F[:, 0] == 1).sum()), n_filled_500ms=int((F[:, -1] == 1).sum()),
                         n_filled_both=int(both.sum()),
                         both_mean_1ms=float(np.mean(a1[both])) if both.any() else None,
                         both_mean_500ms=float(np.mean(a5[both])) if both.any() else None)
        o["H2c_markout_bps"] = mk
        out["by_rule"][name] = o
    d = {nm: r["fill"][:, 0, q] - r["fill"][:, -1, q] for q, nm in enumerate(RULES)}
    pd_ = d["back"] - d["front"]
    out["H2b_back_minus_front_drop"] = dict(zip(("mean", "ci95"), mean_ci(pd_, t)))
    out["share_left_top_five_by_delay"] = {int(dd): float(r["lost"][:, j].mean()) for j, dd in enumerate(DELAYS_MS)}
    return out


def placebo_h2(r):
    """Robustness item 7 for H2 (Deviation of 2026-11-20). Under each rule the fill values of every
    decision are reordered across delays with the same draws as the H1 placebo (taker.shuffle_rows,
    seed SEED + 1, a fresh generator per rule), then the H2 slope and its bootstrap are computed as in
    summarize. It passes on a day if the interval covers zero under all three rules."""
    from .taker import shuffle_rows
    t = r["t"]; out = dict(n_decisions=int(len(t)), shuffle_seed=SEED + 1, by_rule={})
    for q, name in enumerate(RULES):
        F = r["fill"][:, :, q]
        Fs = shuffle_rows(F)
        beta, ci = slope_blocks(Fs, t)
        b0, ci0 = slope_blocks(F, t)
        out["by_rule"][name] = dict(placebo_H2_slope_fill_per_logms=dict(est=beta, ci95=ci),
                                    interval_covers_zero=bool(ci[0] <= 0 <= ci[1]),
                                    placebo_fill_prob_by_delay={int(d): float(Fs[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
                                    unshuffled_H2_slope_fill_per_logms=dict(est=b0, ci95=ci0))
    out["passes_all_three_rules"] = all(v["interval_covers_zero"] for v in out["by_rule"].values())
    return out


def results(day, prepped=None):
    return {"primary": summarize(run(day, True, prepped=prepped))}


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    guard_day(day)
    max_n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    res = {"primary": summarize(run(day, True, max_n))}
    p = result_path("passive", "passive", day)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: {r: (v["by_rule"][r]["H2_slope_fill_per_logms"], v["by_rule"][r]["fill_prob_by_delay"][1], v["by_rule"][r]["fill_prob_by_delay"][500]) for r in RULES} for k, v in res.items()}, indent=1))
