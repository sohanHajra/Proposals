"""Passive and fixed price follow ups on the dev day, specified on 2026-11-19 before any was run.

  run NAME ...   replay one configuration and keep its per decision arrays in data/derived
  summarize      read the arrays and write results/passive/followups_dev_<day>.json

Configurations are KIND_DECISIONS_TIE with KIND in passive, fixed; DECISIONS in random, msgrid,
signal; TIE in after, before. msgrid is the random decisions floored to the whole millisecond.
The arrays are gitignored. Seeds depend on the decision index, as in passive.py and fixed_price.py.
"""
import json
import os
import sys
import time
import numpy as np

from .paths import ROOT, result_path, guard_day
from . import passive, fixed_price
from .passive import RULES
from .fixed_price import STATES, slope_blocks
from .taker import DELAYS_MS, make_decisions
from .signals import make_signal_decisions, frozen_threshold
from .stats import group_mean, contribution, unmatched_diff, NBOOT
from .taker import mean_ci

DERIVED = ROOT / "data" / "derived"
CONFIGS = [f"{k}_{d}_{tie}" for k in ("passive", "fixed") for d in ("random", "msgrid", "signal") for tie in ("after", "before")]


def decisions(book, which):
    t, side, ngaps = make_decisions(book)
    if which == "random":
        return t, side, ngaps
    if which == "msgrid":
        return t - t % 1000, side, ngaps
    ts, ss, ng, thr = make_signal_decisions(book, frozen_threshold())
    return ts, ss, ng


def run_configs(day, names, prepped=None):
    DERIVED.mkdir(parents=True, exist_ok=True)
    prepped = prepped if prepped is not None else passive.prep_day(day)
    for name in names:
        path = DERIVED / f"{name}_{day}.npz"
        if path.exists():
            print("have", name); continue
        kind, which, tie = name.split("_")
        dec = decisions(prepped[0], which)
        t0 = time.time()
        if kind == "passive":
            r = passive.run(day, tie == "after", decisions=dec, prepped=prepped)
        else:
            r = fixed_price.run(day, tie_after=(tie == "after"), decisions=dec, prepped=prepped)
            r.pop("i", None)
        r["ngaps"] = np.array(r["ngaps"])
        np.savez(path, **r)
        print(name, len(r["t"]), round(time.time() - t0), "s", flush=True)


def load(name, day):
    return dict(np.load(DERIVED / f"{name}_{day}.npz"))


def matched_markouts(r, key="m10"):
    """H2c on decisions that filled at both 1 ms and 500 ms, and the unmatched comparison."""
    t = r["t"]; out = {}
    for q, nm in enumerate(RULES):
        F = r["fill"][:, :, q]; M = r[key][:, :, q]
        both = (F[:, 0] == 1) & (F[:, -1] == 1)
        dlt = np.where(both, M[:, -1] - M[:, 0], np.nan)
        out[nm] = dict(matched_500_minus_1=group_mean(dlt, both, t),
                       matched_mean_1ms=group_mean(M[:, 0], both, t)["mean"],
                       matched_mean_500ms=group_mean(M[:, -1], both, t)["mean"],
                       unmatched_500_minus_1=unmatched_diff(np.where(F[:, 0] == 1, M[:, 0], np.nan),
                                                            np.where(F[:, -1] == 1, M[:, -1], np.nan), t))
    return out


def state_costs(r):
    """Fixed price post then cross cost by arrival state with intervals, and a paired trace of the
    change from 1 ms to 500 ms split by the state each decision is in at 500 ms."""
    t = r["t"]; st = r["state"]; out = {}
    for q, nm in enumerate(RULES):
        C = r["cost"][:, :, q]
        by = {}
        for j, d in enumerate(DELAYS_MS):
            by[int(d)] = {s: group_mean(C[:, j], st[:, j] == k, t) for k, s in enumerate(STATES)}
        dlt = C[:, -1] - C[:, 0]
        trace = {s: contribution(dlt, st[:, -1] == k, t) for k, s in enumerate(STATES)}
        tot = mean_ci(dlt, t)
        out[nm] = dict(cost_by_delay_and_state=by,
                       cost_500_minus_1_total=dict(mean=tot[0], ci95=tot[1]),
                       cost_500_minus_1_contribution_by_state_at_500ms=trace,
                       contributions_sum=float(sum(v["contribution"] for v in trace.values())))
    return out


def drop_marketable(r):
    """Exploratory. H5 slope again after leaving out every decision that is marketable on arrival
    at any delay. This keeps or drops a decision by an outcome of delay, so it is a description."""
    t = r["t"]; mk = (r["state"] == STATES.index("marketable")).any(1)
    keep = ~mk; out = dict(n_dropped=int(mk.sum()), n_kept=int(keep.sum()))
    for q, nm in enumerate(RULES):
        C = r["cost"][keep][:, :, q]
        b, ci = slope_blocks(C, t[keep])
        out[nm] = dict(slope_bps_per_logms=dict(est=b, ci95=ci),
                       cost_by_delay={int(d): float(C[:, j].mean()) for j, d in enumerate(DELAYS_MS)})
    return out


def tie_compare(ra, rb, kind):
    t = ra["t"]; assert (t == rb["t"]).all()
    out = dict(n_decisions=int(len(t)))
    for q, nm in enumerate(RULES):
        Fa, Fb = ra["fill"][:, :, q], rb["fill"][:, :, q]
        Ca, Cb = ra["cost"][:, :, q], rb["cost"][:, :, q]
        sa, ca = slope_blocks(Fa, t); sb, cb = slope_blocks(Fb, t)
        xa, xca = slope_blocks(Ca, t); xb, xcb = slope_blocks(Cb, t)
        ch = (Fa != Fb) | (np.abs(Ca - Cb) > 1e-12)
        out[nm] = dict(share_cells_changed=float(ch.mean()),
                       fill_slope_after=dict(est=sa, ci95=ca), fill_slope_before=dict(est=sb, ci95=cb),
                       cost_slope_after=dict(est=xa, ci95=xca), cost_slope_before=dict(est=xb, ci95=xcb),
                       fill_prob_after={int(d): float(Fa[:, j].mean()) for j, d in enumerate(DELAYS_MS)},
                       fill_prob_before={int(d): float(Fb[:, j].mean()) for j, d in enumerate(DELAYS_MS)})
    return out


def summarize(day, root=None):
    res = dict(day=day, nboot=NBOOT)
    pr = load("passive_random_after", day)
    fr = load("fixed_random_after", day)
    rt = lambda x: json.loads(json.dumps(x))         # int keys become strings, as in the files
    res["rerun_check"] = dict(
        passive=rt(passive.summarize(pr)) == json.loads(result_path("passive", "passive", day, root).read_text())["primary"],
        fixed=rt(fixed_price.summarize(fr)) == json.loads(result_path("passive", "fixed_price", day, root).read_text())["random_decisions"])
    res["H2c_matched_passive_random"] = dict(m10=matched_markouts(pr, "m10"), m1=matched_markouts(pr, "m1"))
    res["H2c_matched_fixed_price_random_exploratory"] = dict(m10=matched_markouts(fr, "m10"))
    res["fixed_price_state_costs_random"] = state_costs(fr)
    res["fixed_price_drop_marketable_random_exploratory"] = drop_marketable(fr)
    for kind in ("passive", "fixed"):
        for which in ("random", "msgrid", "signal"):
            a, b = f"{kind}_{which}_after", f"{kind}_{which}_before"
            if (DERIVED / f"{a}_{day}.npz").exists() and (DERIVED / f"{b}_{day}.npz").exists():
                res[f"tie_flip_{kind}_{which}"] = tie_compare(load(a, day), load(b, day), kind)
    ps = load("passive_signal_after", day); fs = load("fixed_signal_after", day)
    res["signal_passive"] = passive.summarize(ps)
    res["signal_passive"]["H2c_matched"] = matched_markouts(ps, "m10")
    res["signal_fixed_price"] = fixed_price.summarize(fs)
    res["signal_fixed_price"]["state_costs"] = state_costs(fs)
    res["signal_fixed_price"]["drop_marketable_exploratory"] = drop_marketable(fs)
    p = result_path("passive", "followups", day, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res["rerun_check"]))
    return res


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-09-01"
    guard_day(day)
    if sys.argv[2] == "run":
        run_configs(day, sys.argv[3:] or CONFIGS)
    else:
        summarize(day)
