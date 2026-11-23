"""The C2 placebo over 200 shuffles on 2026-09-01, for each source (Deviation of 2026-11-23, afternoon, item 4).

Same check as 01's dev day calibration. Seeds SEED + 1 + k for k = 0..199, k = 0 being the registered
shuffle. One permutation of the nine delays per kept decision, the same under all three rules, then the
C2 slope with the 5 minute block bootstrap (2,000 resamples, seed SEED). Calibrated if at most 17 of the
200 intervals exclude zero. Build day only, each source once.

  python -m s2fb.placebo_calibration SOURCE SYM
"""
import json
import sys

import numpy as np

from . import paths  # noqa: F401
from .analysis import keep_mask
from .days import BUILD_DAY
from .guard import Refused
from .paths import RESULTS
from .run import array_file, unit_file
from s2f.passive import RULES
from s2f.taker import SEED
from s2f.placebo_calibration import Slope, perms, NSHUF, NBOOT, MAX_EXCLUDING


def calibrate(r, nshuf=NSHUF):
    keep = keep_mask(r); t = r["t"][keep]; C = r["cost"][keep]; n = len(t)
    sl = Slope(t); rows = np.arange(n)[:, None]
    out = dict(n_kept=int(n), n_shuffles=nshuf, shuffle_seeds=[SEED + 1, SEED + nshuf], bootstrap_resamples=NBOOT,
               rule=f"calibrated if at most {MAX_EXCLUDING} of {nshuf} intervals exclude zero",
               by_rule={nm: dict(slope=[], ci95=[]) for nm in RULES})
    for k in range(nshuf):
        P = perms(n, SEED + 1 + k)
        for q, nm in enumerate(RULES):
            est, ci = sl(C[:, :, q][rows, P])
            out["by_rule"][nm]["slope"].append(est); out["by_rule"][nm]["ci95"].append(ci)
    for nm in RULES:
        o = out["by_rule"][nm]; s = np.array(o["slope"])
        above = int(sum(c[0] > 0 for c in o["ci95"])); below = int(sum(c[1] < 0 for c in o["ci95"]))
        o["summary"] = dict(count_excluding_zero=above + below, count_above=above, count_below=below,
                            calibrated=bool(above + below <= MAX_EXCLUDING), mean_slope=float(s.mean()),
                            sd_slope=float(s.std(ddof=1)), share_positive=float((s > 0).mean()),
                            k0_slope=float(s[0]), k0_rank_from_top=int((s > s[0]).sum()) + 1)
    return out


def main(source, sym):
    f = RESULTS / "build" / "placebo_calibration" / f"{source}_{sym}_{BUILD_DAY}.json"
    if f.exists():
        raise Refused(f"{f} exists")
    r = dict(np.load(array_file(source, sym, BUILD_DAY, "c2_after")))
    res = dict(source=source, symbol=sym, day=BUILD_DAY, **calibrate(r))
    reg = json.loads(unit_file(source, sym, BUILD_DAY, "build", "c2").read_text())["C2"]["placebo"]
    res["k0_matches_registered"] = {nm: res["by_rule"][nm]["slope"][0] == reg[nm]["slope_bps_per_logms"]["est"]
                                    and res["by_rule"][nm]["ci95"][0] == reg[nm]["slope_bps_per_logms"]["ci95"]
                                    for nm in RULES}
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(res, indent=1, default=float))
    print("wrote", f, json.dumps({nm: res["by_rule"][nm]["summary"] for nm in RULES}), res["k0_matches_registered"])


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except Refused as e:
        print("Refusing:", e, file=sys.stderr); sys.exit(1)
