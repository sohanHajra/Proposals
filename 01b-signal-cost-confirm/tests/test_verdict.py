import pytest

from s2fb.verdict import tally
from s2fb.guard import Refused


def c1(a=True, b=False, m=True):
    return dict(slope_interval_above_zero=a, slope_interval_below_zero=b, mean_dS_500ms_at_least_0_1=m)


def c2(a=True, b=False, rules=("front", "random", "back")):
    return {nm: dict(slope_interval_above_zero=a, slope_interval_below_zero=b) for nm in rules}


def days(n_good, n_bad=0, n_out=0, bad=None):
    s = {}
    for i in range(n_good):
        s[f"g{i}"] = ("survived", c1(), c2())
    for i in range(n_bad):
        s[f"b{i}"] = ("survived",) + (bad or (c1(a=False), c2(a=False)))
    for i in range(n_out):
        s[f"o{i}"] = ("left_out", None, None)
    return s


def test_ten_of_twelve_holds():
    v = tally(days(10, 2))
    assert v["C1"]["holds"] and v["C2"]["holds"] and not v["underpowered"]


def test_nine_fails():
    v = tally(days(9, 3))
    assert not v["C1"]["holds"] and not v["C2"]["holds"]


def test_one_below_zero_fails():
    v = tally(days(11, 1, bad=(c1(a=False, b=True), c2(a=False, b=True))))
    assert not v["C1"]["holds"] and not v["C2"]["holds"]


def test_dS500_needed_for_c1():
    v = tally(days(10, 2, bad=(c1(), c2())) | {f"g{i}": ("survived", c1(m=False), c2()) for i in range(3)})
    assert not v["C1"]["holds"] and v["C2"]["holds"]


def test_one_rule_failing_fails_c2():
    s = days(12)
    for i in range(3):
        s[f"g{i}"] = ("survived", c1(), {**c2(), "back": dict(slope_interval_above_zero=False, slope_interval_below_zero=False)})
    v = tally(s)
    assert v["C1"]["holds"] and not v["C2"]["back"]["ok"] and not v["C2"]["holds"]


def test_underpowered_and_left_out():
    v = tally(days(9, 0, 3))
    assert v["underpowered"] and v["surviving"] == 9 and len(v["left_out"]) == 3 and not v["C1"]["holds"]


def test_pending_refused():
    s = days(11); s["p"] = ("pending", None, None)
    with pytest.raises(Refused):
        tally(s)
