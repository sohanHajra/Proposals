"""Tally C1 and C2 on the secondary days, one source at a time.

Uses the same per day rules as the verdict (C1: slope interval above zero
and mean dS at 500 ms at least 0.1 bps; C2: slope interval above zero under
each cancellation rule). Secondary days are never pooled or put in a verdict.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "results"
GROUPS = {
    "cs_stress_recent": ["stress", "extra_recent"],
    "tardis_btc": ["first_of_month"],
    "tardis_eth": ["first_of_month_eth"],
    "bybit": ["bybit"],
}


def day_dirs(folders):
    for f in folders:
        for d in sorted((ROOT / f).iterdir()):
            if (d / "c1.json").exists():
                yield d


def tally(folders):
    out = {"days": 0, "c1_holds": 0, "c2_above": {"front": 0, "random": 0, "back": 0},
           "c2_est_below_zero": 0, "c2_covers_zero_days": {"front": [], "random": [], "back": []},
           "c1_slope_min": None, "c1_slope_max": None, "frozen_c1_holds": None}
    slopes = []
    frozen = 0
    has_frozen = False
    for d in day_dirs(folders):
        day = d.name[-10:]
        out["days"] += 1
        w = json.loads((d / "c1.json").read_text())["C1"]["walk"]
        s = w["slope_bps_per_logms"]
        slopes.append(s["est"])
        if s["ci95"][0] > 0 and w["mean_dS_500ms"]["mean"] >= 0.1:
            out["c1_holds"] += 1
        p = json.loads((d / "c2.json").read_text())["C2"]["primary"]
        for k in ("front", "random", "back"):
            x = p[k]["slope_bps_per_logms"]
            if x["ci95"][0] > 0:
                out["c2_above"][k] += 1
            else:
                out["c2_covers_zero_days"][k].append(day)
            if x["est"] < 0:
                out["c2_est_below_zero"] += 1
        fz = d / "c1_frozen.json"
        if fz.exists():
            has_frozen = True
            fw = json.loads(fz.read_text())["C1"]["walk"]
            if fw["slope_bps_per_logms"]["ci95"][0] > 0 and fw["mean_dS_500ms"]["mean"] >= 0.1:
                frozen += 1
    out["c1_slope_min"] = round(min(slopes), 3)
    out["c1_slope_max"] = round(max(slopes), 3)
    if has_frozen:
        out["frozen_c1_holds"] = frozen
    return out


def per_day(folders):
    rows = {}
    for d in day_dirs(folders):
        w = json.loads((d / "c1.json").read_text())["C1"]["walk"]
        p = json.loads((d / "c2.json").read_text())["C2"]["primary"]
        rows[d.name[-10:]] = {
            "c1_holds": int(w["slope_bps_per_logms"]["ci95"][0] > 0 and w["mean_dS_500ms"]["mean"] >= 0.1),
            **{k: int(p[k]["slope_bps_per_logms"]["ci95"][0] > 0) for k in ("front", "random", "back")},
        }
    return rows


def placebo_misses():
    out = []
    for g, folders in GROUPS.items():
        for d in day_dirs(folders):
            c1 = json.loads((d / "c1.json").read_text())["C1"]["placebo"]["interval_covers_zero"]
            if not c1:
                out.append(f"{g} {d.name[-10:]} C1")
            c2 = json.loads((d / "c2.json").read_text())["C2"]["placebo"]["interval_covers_zero"]
            for k in ("front", "random", "back"):
                if not c2[k]:
                    out.append(f"{g} {d.name[-10:]} C2 {k}")
    return out


def bybit_frozen():
    own, frozen = [], []
    for d in day_dirs(GROUPS["bybit"]):
        own.append(json.loads((d / "c1.json").read_text())["C1"]["walk"]["slope_bps_per_logms"]["est"])
        frozen.append(json.loads((d / "c1_frozen.json").read_text())["C1"]["walk"]["slope_bps_per_logms"]["est"])
    return {"slope_min": round(min(frozen), 3), "slope_max": round(max(frozen), 3),
            "days_frozen_higher": sum(f > o for f, o in zip(frozen, own)), "days": len(own)}


def main():
    res = {g: tally(f) for g, f in GROUPS.items()}
    res["all_days"] = sum(r["days"] for r in res.values())
    res["all_c1_holds"] = sum(r["c1_holds"] for k, r in res.items() if isinstance(r, dict))
    res["per_day_cs"] = per_day(GROUPS["cs_stress_recent"])
    res["bybit_frozen"] = bybit_frozen()
    pm = placebo_misses()
    res["placebo_misses"] = pm
    res["placebo_miss_count"] = len(pm)
    res["placebo_intervals"] = res["all_days"] * 4
    dest = ROOT / "secondary" / "summary.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
