import numpy as np

from s2fb import analysis
from s2f import fixed_price
from s2f.replay import Book


def toy():
    # asks at 101 (size 1) until 1_000_500 us, then 102. Snapshot five levels 101..105 then 102..106
    ts = np.array([0, 1_000_500], np.int64)
    book = Book(ts, np.array([100.0, 100.0]), np.array([1.0, 1.0], np.float32),
                np.array([101.0, 102.0]), np.array([1.0, 1.0], np.float32))
    asks = np.array([[101, 102, 103, 104, 105], [102, 103, 104, 105, 106]], float)
    bids = np.array([[100, 99, 98, 97, 96]] * 2, float)
    # buy like prices, as prep_day stores them. S[1] is the bid side, S[-1] the ask side times minus one
    S = {1: dict(snap_ts=ts, snap_px=bids, snap_q=np.ones((2, 5))),
         -1: dict(snap_ts=ts, snap_px=-asks, snap_q=np.ones((2, 5)))}
    return book, S


def test_race_takes_the_book_one_ms_later_when_the_touch_is_gone():
    book, S = toy()
    t = np.array([1_000_000], np.int64); side = np.array([1])
    r = analysis.race_arrays(book, S, t, side, 0.01)
    # arrivals at 1.001 s and later already see 102, so 1 ms later is the same. At 1 ms delay
    # (arrival 1.001 s) the touch was 102 at arrival, kept. The 1 ms race check at
    # arrival 1_000_000 + 1000 = 1_001_000 vs 1_002_000 both see 102.
    assert r["kept"][0, 0]
    t2 = np.array([999_000], np.int64)       # arrival at 1 ms is 1_000_000 sees 101, 1 ms later 102
    r2 = analysis.race_arrays(book, S, t2, side, 0.01)
    assert not r2["kept"][0, 0] and r2["worse"][0, 0]
    assert r2["S"][0, 0] > 0


def test_order_size_patch_is_put_back():
    q0, d0 = fixed_price.QTY, fixed_price.arrival_state.__defaults__
    with analysis.order_size(0.25):
        assert fixed_price.QTY == 0.25 and fixed_price.arrival_state.__defaults__ == (0.25,)
    assert fixed_price.QTY == q0 and fixed_price.arrival_state.__defaults__ == d0
