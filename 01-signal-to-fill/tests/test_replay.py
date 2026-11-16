import numpy as np
from s2f.replay import Book, Trades, merged_events, book_index_at, taker_fill, mid_at


def mk():
    ts = np.array([1000, 2000, 3000], dtype=np.int64)
    return Book(ts, np.array([99., 99., 100.]), np.array([5., 5., 5.]),
                np.array([101., 102., 103.]), np.array([2., 3., 4.]))


def test_trades_before_book_at_same_time():
    b = mk()
    tr = Trades(np.array([2000, 2500]), np.array([1, -1]), np.array([102., 99.]), np.array([1., 1.]))
    seq = list(merged_events(b, tr))
    assert seq == [("B", 0), ("T", 0), ("B", 1), ("T", 1), ("B", 2)] or seq.index(("T", 0)) < seq.index(("B", 1))
    assert seq.index(("T", 0)) < seq.index(("B", 1))


def test_tie_rule_after_sees_update_at_arrival():
    b = mk()
    assert book_index_at(b, 2000, True) == 1
    assert book_index_at(b, 2000, False) == 0


def test_nothing_seen_before_first_update():
    b = mk()
    assert book_index_at(b, 500) == -1
    assert np.isnan(taker_fill(b, 0, 100, 1, 1.0)["px"])


def test_taker_buy_pays_ask_after_delay():
    b = mk()
    f = taker_fill(b, 1500, 600, 1, 1.0)   # arrives 2100, sees ask 102
    assert f["px"] == 102. and f["filled"] == 1.0
    f0 = taker_fill(b, 1500, 100, 1, 1.0)  # arrives 1600, sees ask 101
    assert f0["px"] == 101.


def test_taker_sell_hits_bid_and_flags_size():
    b = mk()
    f = taker_fill(b, 2500, 600, -1, 9.0)  # arrives 3100, bid 100 qty 5
    assert f["px"] == 100. and f["filled"] == 5.0


def test_mid_and_monotone_ordering():
    b = mk()
    assert mid_at(b, 3000) == 101.5
    assert np.all(np.diff(b.ts) >= 0)
