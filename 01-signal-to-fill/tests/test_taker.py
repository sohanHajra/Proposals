import numpy as np
from s2f.replay import Book
from s2f import taker


def toy_book():
    ts = np.arange(0, 2_000_000_000, 1000, dtype=np.int64)  # one update per ms for 2000 s
    mid = 100 + 0.001 * np.arange(len(ts))
    return Book(ts, mid - 0.05, np.full(len(ts), 5.0, np.float32), mid + 0.05, np.full(len(ts), 5.0, np.float32))


def test_decisions_are_reproducible_and_inside_day():
    b = toy_book()
    t1, s1, _ = taker.make_decisions(b)
    t2, s2, _ = taker.make_decisions(b)
    assert (t1 == t2).all() and (s1 == s2).all()
    assert t1.min() >= b.ts[0] and t1.max() < b.ts[-1]


def test_rising_book_makes_buys_pay_more_with_delay():
    b = toy_book()
    t, side, _ = taker.make_decisions(b)
    buy = side > 0
    mid0 = 0.5 * (b.bid_px + b.ask_px)
    k0 = np.searchsorted(b.ts, t, side="right") - 1
    for dms, expect in [(1, 0.001), (500, 0.5)]:
        k = np.searchsorted(b.ts, t + dms * 1000, side="right") - 1
        gain = (b.ask_px[k] - b.ask_px[k0])[buy]
        assert np.allclose(gain, expect, atol=1e-6)


def test_slope_zero_when_no_delay_effect():
    t = np.arange(0, 3600 * 10**6, 10**7, dtype=np.int64)
    est, ci = taker.slope_blocks(np.zeros((len(t), len(taker.DELAYS_MS))), t, nboot=50)
    assert est == 0 and ci == [0.0, 0.0]
