"""Calibration of the H2 placebo on the dev day (exploratory, lab notebook entry of 2026-11-20).

The registered placebo (passive.placebo_h2) is one shuffle, seed SEED + 1. This repeats it with
seeds SEED + 1 + k for k = 0..NSHUF-1, under each cancellation rule, with the same slope and the same
5 minute block bootstrap (2,000 resamples, seed SEED). k = 0 is the registered shuffle.
It does not touch passive.placebo_h2 or its step in run_test_day.

  python -m s2f.placebo_calibration 2026-09-01
"""
import json
import sys
import numpy as np

from .paths import result_path, guard_day
from .passive import RULES
from .taker import DELAYS_MS, SEED, BLOCK_US

NSHUF = 200
NBOOT = 2000
MAX_EXCLUDING = 17


def perms(n, seed, nd=len(DELAYS_MS)):
    """The permutations shuffle_rows draws with a fresh generator seeded `seed`, one row per decision."""
    rng = np.random.default_rng(seed)
    return np.stack([rng.permutation(nd) for _ in range(n)])


class Slope:
    """slope_blocks from taker.py with the block structure and bootstrap draws worked out once."""

    def __init__(self, t, nboot=NBOOT, seed=SEED, block_us=BLOCK_US):
        x = np.log(DELAYS_MS.astype(float)); self.xc = x - x.mean(); self.sxx = (self.xc ** 2).sum()
        blk = ((t - t.min()) // block_us).astype(int)
        ub, self.inv = np.unique(blk, return_inverse=True)
        self.nb = len(ub); self.n = len(t)
        bn = np.bincount(self.inv, minlength=self.nb)
        self.idx = np.random.default_rng(seed).integers(0, self.nb, (nboot, self.nb))
        self.den = bn[self.idx].sum(1) * self.sxx

    def __call__(self, F):
        per = (F * self.xc).sum(1)
        bsum = np.bincount(self.inv, per, minlength=self.nb)
        est = per.sum() / (self.n * self.sxx)
        boots = bsum[self.idx].sum(1) / self.den
        return float(est), [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]


def calibrate(r, nshuf=NSHUF):
    t = r["t"]; fill = r["fill"]; n = len(t)
    sl = Slope(t)
    rows = np.arange(n)[:, None]
    out = dict(n_decisions=int(n), n_shuffles=nshuf, shuffle_seeds=[SEED + 1, SEED + nshuf],
               bootstrap=dict(resamples=NBOOT, seed=SEED, block_minutes=BLOCK_US // (60 * 10**6)),
               verdict_rule=f"calibrated if at most {MAX_EXCLUDING} of {nshuf} intervals exclude zero, else biased",
               by_rule={nm: dict(slope=[], ci95=[], excludes_zero=[]) for nm in RULES})
    for k in range(nshuf):
        P = perms(n, SEED + 1 + k)
        for q, nm in enumerate(RULES):
            est, ci = sl(fill[:, :, q][rows, P])
            o = out["by_rule"][nm]
            o["slope"].append(est); o["ci95"].append(ci); o["excludes_zero"].append(bool(ci[0] > 0 or ci[1] < 0))
    for nm in RULES:
        o = out["by_rule"][nm]; s = np.array(o["slope"]); c = int(sum(o["excludes_zero"]))
        o["summary"] = dict(count_excluding_zero=c, share_excluding_zero=c / nshuf,
                            verdict="calibrated" if c <= MAX_EXCLUDING else "biased",
                            mean_slope=float(s.mean()), sd_slope=float(s.std(ddof=1)),
                            slope_p2_5=float(np.percentile(s, 2.5)), slope_p97_5=float(np.percentile(s, 97.5)),
                            count_negative_slope=int((s < 0).sum()),
                            count_excluding_below=int(sum(ci[1] < 0 for ci in o["ci95"])),
                            count_excluding_above=int(sum(ci[0] > 0 for ci in o["ci95"])))
    return out


def main(day, root=None):
    guard_day(day)
    if day != "2026-09-01":
        raise SystemExit("dev day only")
    from .robustness import primary_passive
    from .passive_followups import DERIVED
    f = DERIVED / f"passive_random_after_{day}.npz"
    if not f.exists():
        raise SystemExit(f"{f} missing")
    pr, src = primary_passive(day, None, DERIVED)
    res = dict(day=day, check="placebo_h2_calibration", exploratory=True, passive_arrays_from=src, **calibrate(pr))
    reg = result_path("robustness", "placebo_h2", day, root)
    if reg.exists():
        rj = json.loads(reg.read_text())["by_rule"]
        res["k0_matches_registered_file"] = {
            nm: res["by_rule"][nm]["slope"][0] == rj[nm]["placebo_H2_slope_fill_per_logms"]["est"]
            and res["by_rule"][nm]["ci95"][0] == rj[nm]["placebo_H2_slope_fill_per_logms"]["ci95"]
            for nm in RULES}
    p = result_path("robustness", "placebo_h2_calibration", day, root)
    if p.exists():
        raise SystemExit(f"{p} exists, not overwriting it")
    p.write_text(json.dumps(res, indent=1, default=float))
    print("wrote", p, json.dumps({nm: res["by_rule"][nm]["summary"] for nm in RULES}, indent=1),
          res.get("k0_matches_registered_file"), flush=True)
    return res


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-09-01")
