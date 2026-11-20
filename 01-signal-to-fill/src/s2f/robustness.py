"""Robustness checks 1, 3, 5, 6 and 8 from the preregistration, built as written there.
The choices the text leaves open are fixed in the Deviation of 2026-11-19 near midnight, committed
with this file and before its first run.

They apply to the primary tests, H1 and H2, on the registered random decisions with the primary
tie (my order after every event stamped at or before arrival). H1 is reported under the five level
walk (primary since the Deviation of 2026-11-19 near midnight) and under top of book.

  fees         1. Base tier fees added to the shortfall and to the post then cross cost
  local_order  3. Every file put on local capture time and the whole replay rerun on it
  size_1btc    5. Orders of 1 BTC, taker on the five level walk, passive cross on the walk
  horizon      6. Passive horizon 1 s and 60 s
  blocks15     8. 15 minute blocks in the bootstrap

Usage  python -m s2f.robustness DAY [CHECK ...]
Writes results/robustness/<check>_dev_<day>.json on the dev day and <check>_<day>.json otherwise.
"""
import json
import sys
import numpy as np

from .paths import result_path, guard_day
from . import passive
from .passive import RULES, prep_day
from .taker import DELAYS_MS, SEED, QTY, make_decisions, slope_blocks, mean_ci
from .taker_followups import taker_arrays

# Read on https://www.binance.com/en/fee/futureFee on 2026-11-19, Regular User row, USDT
# contracts, no BNB discount. Frozen here for the test days.
FEES = dict(maker_pct=0.0200, taker_pct=0.0500, maker_bps=2.0, taker_bps=5.0,
            source="https://www.binance.com/en/fee/futureFee", read_on="2026-11-19",
            tier="Regular User, USDT maker and taker, no BNB discount")
BLOCK15_US = 15 * 60 * 10**6
SIZE_BIG = 1.0
HORIZONS_S = (1, 60)
CHECKS = ("fees", "blocks15", "size_1btc", "horizon", "local_order")
J500 = len(DELAYS_MS) - 1


def h1_line(dS, S, t, block_us=None):
    kw = {} if block_us is None else dict(block_us=block_us)
    b, ci = slope_blocks(dS, t, **kw)
    m5, c5 = mean_ci(dS[:, J500], t, **kw)
    return dict(slope_bps_per_logms=dict(est=b, ci95=ci), mean_dS_500ms=dict(mean=m5, ci95=c5),
                mean_S_by_delay_ms={int(d): float(S[:, j].mean()) for j, d in enumerate(DELAYS_MS)})


def taker_h1(book, S, t, side, qty=QTY, block_us=None):
    a = taker_arrays(book, S, t, side, True, qty)
    return dict(n_decisions=int(len(t)), order_size_btc=qty,
                H1_five_level_walk=h1_line(a["dS_walk"], a["S_walk"], t, block_us),
                H1_top_of_book=h1_line(a["dS"], a["S"], t, block_us),
                flag_share_walk_by_delay_ms={int(d): float(a["flag_walk"][:, j].mean()) for j, d in enumerate(DELAYS_MS)},
                flag_share_top_by_delay_ms={int(d): float(a["flag_top"][:, j].mean()) for j, d in enumerate(DELAYS_MS)}), a


def h2_lines(r, block_us=None):
    kw = {} if block_us is None else dict(block_us=block_us)
    t = r["t"]; out = {}
    for q, nm in enumerate(RULES):
        F = r["fill"][:, :, q]; C = r["cost"][:, :, q]
        b, ci = slope_blocks(F, t, **kw)
        cb, cci = slope_blocks(C, t, **kw)
        out[nm] = dict(H2_slope_fill_per_logms=dict(est=b, ci95=ci),
                       post_then_cross_cost_slope_bps_per_logms=dict(est=cb, ci95=cci))
    return out


def primary_passive(day, prepped, derived=None):
    """The primary passive arrays. Taken from the saved follow up run when it exists (that run is
    checked against the registered passive results there), else replayed here."""
    from . import passive_followups
    d = passive_followups.DERIVED if derived is None else derived
    f = d / f"passive_random_after_{day}.npz"
    if f.exists():
        return dict(np.load(f)), str(f.name)
    return passive.run(day, True, prepped=prepped), "replayed"


def check_fees(day, prepped, pr):
    book, tr, S = prepped
    t, side, _ = make_decisions(book)
    a = taker_arrays(book, S, t, side, True, QTY)
    out = dict(fees=FEES, n_decisions=int(len(t)))
    for name, key in (("five_level_walk", "S_walk"), ("top_of_book", "S")):
        Sf = a[key] + FEES["taker_bps"]
        dSf = Sf - Sf[:, [0]]
        out["H1_" + name] = h1_line(dSf, Sf, t)
        out["H1_" + name]["max_abs_change_in_dS_from_fees"] = float(np.abs(dSf - (a[key] - a[key][:, [0]])).max())
    tp = pr["t"]; out["passive"] = {}
    for q, nm in enumerate(RULES):
        f = pr["frac"][:, :, q]
        C = pr["cost"][:, :, q] + f * FEES["maker_bps"] + (1 - f) * FEES["taker_bps"]
        cb, cci = slope_blocks(C, tp)
        dm, dci = mean_ci(C[:, -1] - C[:, 0], tp)
        out["passive"][nm] = dict(post_then_cross_cost_with_fees_by_delay={int(d): float(C[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
                                  post_then_cross_cost_with_fees_slope_bps_per_logms=dict(est=cb, ci95=cci),
                                  cost_with_fees_500ms_minus_1ms=dict(mean=dm, ci95=dci),
                                  fill_prob_unchanged_by_fees=True)
    return out


def check_blocks15(day, prepped, pr):
    book, tr, S = prepped
    t, side, _ = make_decisions(book)
    h1_15, _ = taker_h1(book, S, t, side, QTY, BLOCK15_US)
    h1_5, _ = taker_h1(book, S, t, side, QTY, None)
    return dict(block_minutes=15, nboot=2000, seed=SEED,
                taker_15min=h1_15, taker_5min_same_values=h1_5,
                passive_15min=h2_lines(pr, BLOCK15_US), passive_5min_same_values=h2_lines(pr, None))


def check_size(day, prepped):
    book, tr, S = prepped
    t, side, ngaps = make_decisions(book)
    tk, _ = taker_h1(book, S, t, side, SIZE_BIG)
    r = passive.run(day, True, decisions=(t, side, ngaps), prepped=prepped, qty=SIZE_BIG, cross_walk=True)
    ps = passive.summarize(r)
    ps["cross_beyond_five_levels_share_by_rule"] = {nm: float(r["cross_flag"][:, :, q].mean()) for q, nm in enumerate(RULES)}
    return dict(order_size_btc=SIZE_BIG, taker=tk, passive=ps)


def check_horizon(day, prepped):
    book, tr, S = prepped
    dec = make_decisions(book)
    out = {}
    for h in HORIZONS_S:
        r = passive.run(day, True, decisions=dec, prepped=prepped, h_us=h * 10**6)
        out[f"{h}s"] = passive.summarize(r)
    return dict(horizons_s=list(HORIZONS_S), by_horizon=out)


def check_local(day):
    prepped = prep_day(day, clock="local")
    book, tr, S = prepped
    t, side, ngaps = make_decisions(book)
    tk, _ = taker_h1(book, S, t, side, QTY)
    r = passive.run(day, True, decisions=(t, side, ngaps), prepped=prepped)
    return dict(clock="local_timestamp", feed_gaps_over_1s=int(ngaps), taker=tk, passive=passive.summarize(r))


def run_checks(day, checks=CHECKS, root=None, derived=None, prepped=None):
    """Runs the named checks in the fixed order of CHECKS and writes one file per check."""
    written = []
    need_ex = any(c in checks for c in ("fees", "blocks15", "size_1btc", "horizon"))
    if need_ex and prepped is None:
        prepped = prep_day(day)
    pr = None
    for c in CHECKS:
        if c not in checks:
            continue
        if c in ("fees", "blocks15") and pr is None:
            pr, src = primary_passive(day, prepped, derived)
        if c == "fees":
            res = check_fees(day, prepped, pr)
        elif c == "blocks15":
            res = check_blocks15(day, prepped, pr)
        elif c == "size_1btc":
            res = check_size(day, prepped)
        elif c == "horizon":
            res = check_horizon(day, prepped)
        else:
            res = check_local(day)
        res = dict(day=day, check=c, **res)
        if c in ("fees", "blocks15"):
            res["passive_arrays_from"] = src
        p = result_path("robustness", c, day, root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, indent=1, default=float))
        written.append(p)
        print("wrote", p, flush=True)
    return written


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    guard_day(day)
    which = tuple(sys.argv[2:]) or CHECKS
    bad = [c for c in which if c not in CHECKS]
    if bad:
        sys.exit(f"unknown check {bad}, choose from {CHECKS}")
    run_checks(day, which)
