import numpy as np
from s2f.lobster_rq2 import w1_uniform, dists, level_size


def test_w1_uniform_limits():
    rng = np.random.default_rng(0)
    assert w1_uniform(rng.random(200000)) < 0.005
    assert abs(w1_uniform(np.zeros(10)) - 0.5) < 1e-3
    d = dists(np.ones(10))
    assert d["back"] == 0 and min(d, key=d.get) == "back"


def test_level_size_reads_side():
    row = np.array([101, 5, 99, 7, 102, 3, 98, 2])
    assert level_size(row, -1, 102) == (3, True)
    assert level_size(row, 1, 98) == (2, True)
    assert level_size(row, 1, 97) == (0, False)
