import numpy as np

from s2fb.cryptostruct import Side
from s2fb.audit import gap_rule, day_bounds_us


def test_side_book_best_and_top5():
    b = Side(1)
    for t, q in [(100, 1.0), (99, 2.0), (97, 1.0), (95, 3.0), (90, 1.0), (80, 1.0)]:
        b.set(t, t / 10, q)
    assert b.best == 100 and b.top5() == [100, 99, 97, 95, 90]
    b.set(100, 10.0, 0.0)
    assert b.best == 99 and b.top5() == [99, 97, 95, 90, 80]
    b.set(101, 10.1, 0.5)
    assert b.best == 101
    a = Side(-1)
    for t in (105, 106, 110):
        a.set(t, t / 10, 1.0)
    a.set(105, 10.5, 0.0)
    assert a.best == 106 and a.top5() == [106, 110]


def test_gap_rule():
    lo, hi = day_bounds_us("2026-09-01")
    ts = np.arange(lo, hi, 500_000)
    assert gap_rule(ts, "2026-09-01")["left_out"] is False
    cut = (ts < lo + 3600 * 10**6) | (ts > lo + 7300 * 10**6)
    g = gap_rule(ts[cut], "2026-09-01")
    assert g["left_out"] is True and abs(g["total_gap_s"] - 3700.5) < 1


def test_head_and_tail_count():
    lo, hi = day_bounds_us("2026-09-01")
    ts = np.arange(lo + 1800 * 10**6, hi - 1900 * 10**6, 10**5)
    g = gap_rule(ts, "2026-09-01")
    assert g["left_out"] is True and g["gaps_over_1s"] == 0
