import numpy as np
from s2f import passive, taker, run_test_day as R

US = 10**6


def _arrays(n=600, seed=3):
    rng = np.random.default_rng(seed)
    nd = len(taker.DELAYS_MS)
    t = np.sort(rng.integers(0, 6 * 3600 * US, n)).astype(np.int64)
    # fill falls with delay so the unshuffled slope is clearly negative
    p = np.linspace(0.8, 0.2, nd)
    fill = np.stack([(rng.random((n, nd)) < p).astype(float) for _ in range(3)], axis=2)
    return dict(t=t, fill=fill)


def test_shuffle_keeps_each_decisions_values():
    r = _arrays()
    for q in range(3):
        F = r["fill"][:, :, q]
        Fs = taker.shuffle_rows(F)
        assert Fs.shape == F.shape
        assert np.array_equal(np.sort(Fs, 1), np.sort(F, 1))     # same nine values per decision
        assert np.array_equal(Fs.sum(1), F.sum(1))
        assert not np.array_equal(Fs, F)                          # labels did move
    assert np.array_equal(r["fill"], _arrays()["fill"])           # the input is left alone


def test_same_permutations_as_h1_and_across_rules():
    n, nd = 50, len(taker.DELAYS_MS)
    idx = np.tile(np.arange(nd, dtype=float), (n, 1))
    perm = taker.shuffle_rows(idx).astype(int)                     # the permutation each decision got
    r = _arrays(n)
    for q in range(3):
        F = r["fill"][:, :, q]
        assert np.array_equal(taker.shuffle_rows(F), np.take_along_axis(F, perm, 1))


def test_placebo_flattens_a_real_slope_and_reports_each_rule():
    r = _arrays()
    out = passive.placebo_h2(r)
    assert out["shuffle_seed"] == taker.SEED + 1 and out["n_decisions"] == 600
    for nm in passive.RULES:
        o = out["by_rule"][nm]
        assert o["unshuffled_H2_slope_fill_per_logms"]["ci95"][1] < 0
        lo, hi = o["placebo_H2_slope_fill_per_logms"]["ci95"]
        assert o["interval_covers_zero"] == (lo <= 0 <= hi)
        assert o["unshuffled_H2_slope_fill_per_logms"]["est"] == taker.slope_blocks(r["fill"][:, :, passive.RULES.index(nm)], r["t"])[0]
    assert out["passes_all_three_rules"] == all(v["interval_covers_zero"] for v in out["by_rule"].values())


def test_runner_has_the_h2_placebo_on_test_days_only():
    assert R.STEPS_TEST.index("placebo_h2") == R.STEPS_TEST.index("robustness") + 1
    assert "placebo_h2" not in R.STEPS_BREADTH
    names = [p.name for p in R.outputs("2026-10-01", R.STEPS_TEST, "/tmp/x")]
    assert "placebo_h2_2026-10-01.json" in names
