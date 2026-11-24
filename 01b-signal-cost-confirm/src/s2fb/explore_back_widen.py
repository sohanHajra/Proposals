"""Exploratory, written on 2026-11-23 after the twelve test days were read. Not in the preregistration.

On 2026-09-01 the CryptoStruct back placebo missed zero on 19 of 200 shuffles, so its 95% intervals
act more like 90.5% ones. This asks a rough question. If every back interval on the test days were
wider by the normal ratio z(0.975) / z(1 - 19/400), how many would still sit above zero? It also counts
the registered test day placebo misses. Nothing here feeds the verdict.

  python -m s2fb.explore_back_widen    writes results/exploratory/c2_back_widened.json
"""
import json
from statistics import NormalDist

from .days import TEST_DAYS
from .paths import RESULTS

CAL = RESULTS / "build" / "placebo_calibration" / "cryptostruct_BTCUSDT_2026-09-01.json"


def main():
    cal = json.loads(CAL.read_text())["by_rule"]["back"]["summary"]["count_excluding_zero"]
    n = 200
    z = NormalDist().inv_cdf
    ratio = z(0.975) / z(1 - cal / n / 2)
    days, above, placebo_miss = {}, 0, {"front": 0, "random": 0, "back": 0}
    for d in TEST_DAYS:
        c2 = json.loads((RESULTS / "test" / f"cryptostruct_BTCUSDT_{d}" / "c2.json").read_text())["C2"]
        s = c2["primary"]["back"]["slope_bps_per_logms"]
        lo = s["est"] - ratio * (s["est"] - s["ci95"][0])
        hi = s["est"] + ratio * (s["ci95"][1] - s["est"])
        days[d] = dict(est=s["est"], ci95=s["ci95"], widened=[lo, hi])
        above += lo > 0
        for r in placebo_miss:
            plo, phi = c2["placebo"][r]["slope_bps_per_logms"]["ci95"]
            placebo_miss[r] += plo > 0 or phi < 0
    out = dict(calibration_back_misses=cal, shuffles=n, ratio=ratio, back_above_zero_widened=above,
               min_widened_lower=min(v["widened"][0] for v in days.values()),
               min_widened_lower_day=min(days, key=lambda d: days[d]["widened"][0] if days[d]["widened"][0] > 0 else 9),
               placebo_test_day_misses=placebo_miss, placebo_test_day_misses_total=sum(placebo_miss.values()),
               placebo_intervals=3 * len(TEST_DAYS), days=days)
    f = RESULTS / "exploratory" / "c2_back_widened.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "days"}, indent=1))


if __name__ == "__main__":
    main()
