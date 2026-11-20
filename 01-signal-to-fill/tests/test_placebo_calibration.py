import numpy as np
from s2f import placebo_calibration as pc
from s2f.taker import DELAYS_MS, SEED, shuffle_rows, slope_blocks


def fake(n=600, seed=3):
    rng = np.random.default_rng(seed)
    t = np.sort(rng.integers(0, 3 * 3600 * 10**6, n))
    fill = (rng.random((n, len(DELAYS_MS), 3)) < 0.5).astype(float)
    return dict(t=t, fill=fill)


def test_first_seed_is_the_registered_shuffle_and_slope():
    r = fake()
    out = pc.calibrate(r, nshuf=3)
    for q, nm in enumerate(("front", "random", "back")):
        est, ci = slope_blocks(shuffle_rows(r["fill"][:, :, q]), r["t"])
        assert out["by_rule"][nm]["slope"][0] == est
        assert out["by_rule"][nm]["ci95"][0] == ci


def test_later_seeds_differ_and_keep_each_row():
    r = fake()
    P0, P1 = pc.perms(50, SEED + 1), pc.perms(50, SEED + 2)
    assert (P0 != P1).any()
    assert all(sorted(p) == list(range(len(DELAYS_MS))) for p in P1)
    out = pc.calibrate(r, nshuf=4)
    s = out["by_rule"]["random"]["summary"]
    assert len(out["by_rule"]["random"]["slope"]) == 4
    assert s["count_excluding_zero"] == s["count_excluding_below"] + s["count_excluding_above"]
    assert s["verdict"] in ("calibrated", "biased")
