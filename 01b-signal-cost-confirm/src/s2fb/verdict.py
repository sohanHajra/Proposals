"""The C1 and C2 verdicts on BTCUSDT from the per day files (Deviation of 2026-11-23, afternoon, item 5).

C1 holds if the slope interval is above zero on at least 10 surviving test days and below zero on none,
and mean walk dS(500 ms) is at least 0.1 bps on at least 10 surviving test days.
C2 holds if under each of the three rules the slope interval is above zero on at least 10 surviving test
days and below zero on none. A day is left out by its audit (gap rule or a failed file). Fewer than ten
surviving days means the verdicts are reported as underpowered.

  python -m s2fb.verdict        writes results/verdict/verdict_BTCUSDT.json once every test day is done
"""
import json
import sys

from .days import TEST_DAYS
from .guard import Refused
from .paths import RESULTS

NEED = 10
RULES = ("front", "random", "back")


def day_state(day, results=RESULTS, source="cryptostruct", sym="BTCUSDT", role="test"):
    f = results / role / f"{source}_{sym}_{day}"
    a = f / "audit.json"
    if a.exists() and json.loads(a.read_text())["gap_rule"]["left_out"]:
        return "left_out", None, None
    if (f / "c1.json").exists() and (f / "c2.json").exists():
        return "survived", json.loads((f / "c1.json").read_text())["C1"]["day_counts"], \
            json.loads((f / "c2.json").read_text())["C2"]["day_counts"]
    return "pending", None, None


def tally(states):
    """states: {day: (state, c1 day_counts, c2 day_counts)} for every test day."""
    pending = [d for d, s in states.items() if s[0] == "pending"]
    if pending:
        raise Refused(f"test days not finished: {pending}")
    surv = {d: s for d, s in states.items() if s[0] == "survived"}
    n = len(surv)
    c1 = dict(above=sum(s[1]["slope_interval_above_zero"] for s in surv.values()),
              below=sum(s[1]["slope_interval_below_zero"] for s in surv.values()),
              dS500_at_least_0_1=sum(s[1]["mean_dS_500ms_at_least_0_1"] for s in surv.values()))
    c1["holds"] = c1["above"] >= NEED and c1["below"] == 0 and c1["dS500_at_least_0_1"] >= NEED
    c2 = {nm: dict(above=sum(s[2][nm]["slope_interval_above_zero"] for s in surv.values()),
                   below=sum(s[2][nm]["slope_interval_below_zero"] for s in surv.values())) for nm in RULES}
    for v in c2.values():
        v["ok"] = v["above"] >= NEED and v["below"] == 0
    c2["holds"] = all(c2[nm]["ok"] for nm in RULES)
    return dict(test_days=len(states), surviving=n, left_out=sorted(d for d, s in states.items() if s[0] == "left_out"),
                underpowered=n < NEED, need=NEED, C1=c1, C2=c2)


def main():
    out = tally({d: day_state(d) for d in TEST_DAYS})
    f = RESULTS / "verdict" / "verdict_BTCUSDT.json"
    if f.exists():
        raise Refused(f"{f} exists")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Refused as e:
        print("Refusing:", e, file=sys.stderr); sys.exit(1)
