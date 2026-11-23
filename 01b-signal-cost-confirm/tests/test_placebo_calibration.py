import numpy as np

from s2fb.placebo_calibration import calibrate
from s2fb.analysis import c2_lines
from s2f.fixed_price import STATES


def test_first_seed_is_the_registered_placebo():
    rng = np.random.default_rng(1)
    n = 400
    r = dict(t=np.sort(rng.integers(0, 6 * 3600 * 10**6, n)), cost=rng.normal(size=(n, 9, 3)),
             frac=rng.uniform(size=(n, 9, 3)), state=np.full((n, 9), [i for i in range(len(STATES)) if STATES[i] != "marketable"][0]))
    r["state"][:20, 3] = STATES.index("marketable")
    reg = c2_lines(r, placebo=True)
    out = calibrate(r, nshuf=3)
    for nm in ("front", "random", "back"):
        assert out["by_rule"][nm]["slope"][0] == reg[nm]["slope_bps_per_logms"]["est"]
        assert out["by_rule"][nm]["ci95"][0] == reg[nm]["slope_bps_per_logms"]["ci95"]
    assert out["n_kept"] == 380
