"""Summarise the registered secondary checks across the twelve test days.

Reads the per day c1.json and c2.json the runner wrote and reports ranges and
counts for the race rule, the tie flip, 15 minute blocks, fees and the placebo,
next to the primary numbers. Nothing here feeds the verdict.
"""
import json
from pathlib import Path

from s2fb.days import TEST_DAYS

ROOT = Path(__file__).resolve().parents[2] / "results"
RULES = ("front", "random", "back")


def rng(xs, nd=3):
    return [round(min(xs), nd), round(max(xs), nd)]


def main():
    c1 = {k: {"slope": [], "dS500": [], "lo": []} for k in ("walk", "race", "tie_before", "blocks15")}
    race_changed, race_worse, race_better = [], [], []
    split = []
    fee_level = []
    scale = {r: [] for r in RULES}
    scale_fees = {r: [] for r in RULES}
    tie_same = 0
    c1_placebo_cover = 0
    c2 = {v: {r: {"above": 0, "below": 0, "est": [], "not_above": []} for r in RULES} for v in ("primary", "fees", "blocks15", "tie_before")}
    c2_placebo_cover = {r: 0 for r in RULES}
    n = 0
    for day in TEST_DAYS:
        d = ROOT / "test" / f"cryptostruct_BTCUSDT_{day}"
        if not (d / "c1.json").exists():
            continue
        n += 1
        a = json.loads((d / "c1.json").read_text())["C1"]
        for k in c1:
            s = a[k]["slope_bps_per_logms"]
            c1[k]["slope"].append(s["est"])
            c1[k]["lo"].append(s["ci95"][0])
            c1[k]["dS500"].append(a[k]["mean_dS_500ms"]["mean"])
        race_changed.append(a["race"]["share_cells_changed"])
        race_worse.append(a["race"]["share_cells_worse"])
        race_better.append(a["race"]["share_cells_better"])
        sp = a["split_dS_500ms"]
        split.append({"day": day, "dS500": round(a["walk"]["mean_dS_500ms"]["mean"], 3),
                      "drift": round(sp["drift"]["mean"], 3), "arrival": round(sp["arrival"]["mean"], 3)})
        fee_level.append(a["fees"]["mean_S_500ms_with_fees"])
        c1_placebo_cover += bool(a["placebo"]["interval_covers_zero"])
        b = json.loads((d / "c2.json").read_text())["C2"]
        for v in c2:
            for r in RULES:
                s = b[v][r]["slope_bps_per_logms"]
                c2[v][r]["est"].append(s["est"])
                c2[v][r]["above"] += s["ci95"][0] > 0
                c2[v][r]["below"] += s["ci95"][1] < 0
                if not s["ci95"][0] > 0:
                    c2[v][r]["not_above"].append(day)
                if v in ("primary", "fees"):
                    cb = b[v][r]["cost_by_delay"]
                    (scale if v == "primary" else scale_fees)[r].append(cb["500"] - cb["1"])
        tie_same += all(b["tie_before"][r]["slope_bps_per_logms"] == b["primary"][r]["slope_bps_per_logms"] for r in RULES)
        for r in RULES:
            c2_placebo_cover[r] += bool(b["placebo"]["interval_covers_zero"][r])
    out = {"days": n, "C1": {}, "C2": {}}
    for k, v in c1.items():
        out["C1"][k] = {"slope_range": rng(v["slope"]), "dS500_range": rng(v["dS500"], 2),
                        "slope_above_zero": sum(x > 0 for x in v["lo"])}
    out["C1"]["race"]["share_cells_changed_range"] = rng(race_changed, 3)
    out["C1"]["race"]["share_cells_worse_range"] = rng(race_worse, 3)
    out["C1"]["race"]["pct_cells_changed_range"] = [round(100 * min(race_changed)), round(100 * max(race_changed))]
    out["C1"]["race"]["pct_cells_worse_range"] = [round(100 * min(race_worse), 1), round(100 * max(race_worse), 1)]
    out["C1"]["race"]["pct_cells_better_range"] = [round(100 * min(race_better), 2), round(100 * max(race_better), 2)]
    out["C1"]["placebo_covers_zero"] = c1_placebo_cover
    out["C1"]["split_by_day"] = split
    out["C1"]["split_drift_range"] = rng([s["drift"] for s in split], 2)
    out["C1"]["split_arrival_range"] = rng([s["arrival"] for s in split], 3)
    out["C1"]["drift_above_dS500_days"] = sum(s["drift"] > s["dS500"] for s in split)
    out["C1"]["fees_mean_S500_range"] = rng(fee_level, 2)
    out["C2"]["tie_identical_days"] = tie_same
    out["C2_cost_1_to_500ms"] = {r: rng(x, 3) for r, x in scale.items()}
    out["C2_cost_1_to_500ms_with_fees"] = {r: rng(x, 3) for r, x in scale_fees.items()}
    for v, rr in c2.items():
        out["C2"][v] = {r: {"above": x["above"], "below": x["below"], "slope_range": rng(x["est"], 4),
                         "days_not_above": x["not_above"]} for r, x in rr.items()}
    out["C2"]["placebo_covers_zero"] = c2_placebo_cover
    dest = ROOT / "verdict" / "checks_BTCUSDT.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
