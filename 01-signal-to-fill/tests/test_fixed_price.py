import numpy as np
from s2f.fixed_price import arrival_state, pooled_slope
from s2f.passive import walk, T_TRADE, T_TICK, T_SNAP
from s2f.taker import DELAYS_MS

SNAP = np.array([101.0, 100.0, 99.0, 98.0, 97.0])
SQ = np.array([1.0, 2.0, 3.0, 4.0, 5.0])


def test_marketable_fills_touch_as_taker():
    # buy like price 100, the other side now offers at 100 with 0.004, so 0.004 fills at once
    st, tq, ahead, above = arrival_state(100.0, 99.9, 1.0, 100.0, 0.004, SNAP, SQ)
    assert st == "marketable" and tq == 0.004 and ahead == 0.0 and not above
    st, tq, _, _ = arrival_state(100.0, 99.9, 1.0, 99.8, 5.0, SNAP, SQ)
    assert st == "marketable" and tq == 0.01


def test_joins_when_best_unchanged():
    st, tq, ahead, above = arrival_state(100.0, 100.0, 1.5, 100.1, 2.0, SNAP, SQ)
    assert (st, tq, ahead, above) == ("joins", 0.0, 1.5, False)


def test_inside_when_book_moved_toward_me_without_crossing():
    st, _, ahead, _ = arrival_state(100.0, 99.9, 1.5, 100.1, 2.0, SNAP, SQ)
    assert st == "inside" and ahead == 0.0


def test_behind_new_best_uses_snapshot_size():
    st, _, ahead, above = arrival_state(100.0, 101.0, 1.0, 101.1, 2.0, SNAP, SQ)
    assert st == "behind" and ahead == 2.0 and above


def test_below_top_five_counts_as_lost():
    st, _, _, _ = arrival_state(96.0, 101.0, 1.0, 101.1, 2.0, SNAP, SQ)
    assert st == "below_top_five"


def test_behind_order_fills_only_if_price_comes_back():
    # behind a better best: trades at 101 do nothing, then the best falls back to my level
    k = np.array([T_TRADE, T_TICK, T_TRADE, T_TRADE]); a = np.array([101.0, 100.0, 100.0, 100.0])
    b = np.array([5.0, 1.0, 1.0, 0.01])
    sp = np.zeros((4, 5)); sq = np.zeros((4, 5))
    f, _, lost = walk(100.0, 2.0, k, a, b, sp, sq, np.random.default_rng(1), best_above0=True)
    # the tick at 100 shows 1.0 displayed, so 1.0 of the 2.0 ahead is gone under every rule
    # (nothing joined behind me), the trade of 1.0 clears the rest and 0.01 fills me
    assert lost == -1 and (f == 0.01).all()
    f2, _, _ = walk(100.0, 2.0, k[:1], a[:1], b[:1], sp[:1], sq[:1], np.random.default_rng(1), best_above0=True)
    assert (f2 == 0).all()


def test_pooled_slope_recovers_known_slope():
    rng = np.random.default_rng(0)
    n = 600
    t = np.arange(n, dtype=np.int64) * 10**6
    x = np.log(DELAYS_MS.astype(float))
    Y = 0.5 * x[None, :] + rng.normal(0, 0.01, (n, len(x)))
    Y[rng.random(Y.shape) < 0.3] = np.nan
    est, ci = pooled_slope(Y, t, nboot=200)
    assert abs(est - 0.5) < 0.01 and ci[0] < est < ci[1]
