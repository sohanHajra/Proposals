"""Breadth table across the two test days and six breadth days, as registered on 2026-11-19.

Usage  python -m s2f.breadth

Reads only results files already written by run_test_day. For H1 to H5, H1b, H2b and H2c it takes the
statistic and its interval on each day and counts days where the interval sits on the registered side,
on the opposite side, or covers zero. Consistent if registered side on at least six of eight days and
opposite on none, contradicted if opposite on two or more, mixed otherwise. A day is left out only if
its files are missing (download failed) or its gaps over 1 s add up to more than one hour. The audit
stores the count and the longest gap, so count times longest is used as an upper bound on the total;
if that bound is over an hour the day is flagged for a closer look rather than dropped.
Writes results/breadth/breadth_table.json. Verdicts on H1 to H5 still come from the test days only.
"""
import json
from .paths import RESULTS
from .get_data import TEST_DAYS, BREADTH_DAYS

RULES = ("front", "random", "back")


def _load(p):
    return json.loads((RESULTS / p).read_text())


def stats(day):
    """(name, registered side, est, lo, hi) for every registered statistic on one day."""
    out = []
    t = _load(f"taker/taker_{day}.json")["primary_five_level_walk"]["slope_bps_per_logms"]
    out.append(("H1", "above", t["est"], *t["ci95"]))
    f = _load(f"taker/followups_{day}.json")["random"]
    h = f["H1b_registered"]; out.append(("H1b", "above", h["diff"], *h["ci95"]))
    h = f["RQ3_volatility"]["dS100_high_minus_rest"]; out.append(("H3", "above", h["diff"], *h["ci95"]))
    p = _load(f"passive/passive_{day}.json")["primary"]
    for r in RULES:
        s = p["by_rule"][r]["H2_slope_fill_per_logms"]; out.append((f"H2 {r}", "below", s["est"], *s["ci95"]))
    h = p["H2b_back_minus_front_drop"]; out.append(("H2b", "above", h["mean"], *h["ci95"]))
    pf = _load(f"passive/followups_{day}.json")["H2c_matched_passive_random"]["m10"]
    for r in RULES:
        u = pf[r]["unmatched_500_minus_1"]; out.append((f"H2c {r}", "below", u["diff"], *u["ci95"]))
    fp = _load(f"passive/fixed_price_{day}.json")["random_decisions"]["by_rule"]
    for r in RULES:
        s = fp[r]["H5_post_then_cross_cost_slope_bps_per_logms"]; out.append((f"H5 {r}", "above", s["est"], *s["ci95"]))
    return out


def side(reg, lo, hi):
    if lo > 0:
        s = "above"
    elif hi < 0:
        s = "below"
    else:
        return "covers zero"
    return "registered" if s == reg else "opposite"


def main():
    days, left_out = [], {}
    for d in TEST_DAYS + BREADTH_DAYS:
        try:
            a = _load(f"audit/tardis_{d}.json")
            st = stats(d)
        except FileNotFoundError as e:
            left_out[d] = f"missing {e.filename}"; continue
        bound = a["gaps_over_1s_bt"] * a["max_gap_s_bt_local"]
        if bound > 3600:
            left_out[d] = f"gap bound {bound:.0f} s over one hour, check total"; continue
        days.append((d, st, bound))
    table = {}
    for d, st, _ in days:
        for name, reg, est, lo, hi in st:
            table.setdefault(name, {"registered_side": reg, "by_day": {}})["by_day"][d] = dict(est=est, ci95=[lo, hi], side=side(reg, lo, hi))
    for name, row in table.items():
        sides = [v["side"] for v in row["by_day"].values()]
        c = {k: sides.count(k) for k in ("registered", "opposite", "covers zero")}
        row["counts"] = c
        row["n_days"] = len(sides)
        row["verdict"] = ("consistent" if c["registered"] >= 6 and c["opposite"] == 0 else
                          "contradicted" if c["opposite"] >= 2 else "mixed")
    res = dict(days_used=[d for d, _, _ in days], gap_bound_s={d: b for d, _, b in days}, left_out=left_out, table=table)
    p = RESULTS / "breadth" / "breadth_table.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=1))
    for name, row in table.items():
        print(f"{name:12s} {row['verdict']:12s} {row['counts']}")
    print("left out", left_out)


if __name__ == "__main__":
    main()
