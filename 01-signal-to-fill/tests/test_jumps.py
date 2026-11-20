import numpy as np
from s2f.replay import Book
from s2f import jumps

MS = 1000


def _book():
    # one row per ms for 2 s, mid 100.05, then an up move of 3 bps inside 4 ms at 1000 ms
    ts = np.arange(0, 2000 * MS, MS, dtype=np.int64)
    bid = np.full(len(ts), 100.0); ask = np.full(len(ts), 100.1)
    up = ts >= 1000 * MS
    bid[up] += 0.03; ask[up] += 0.03
    bq = np.ones(len(ts), np.float32); aq = np.ones(len(ts), np.float32)
    aq[ts == 1002 * MS] = 0.004                       # thin ask 2 ms after the move
    ask[ts >= 1003 * MS] += 0.1                       # ask level gone 3 ms after the move
    return Book(ts, bid, bq, ask, aq)


def test_jump_stamps_find_the_move_and_its_sign():
    b = _book()
    jts, d, mv = jumps.jump_stamps(b, 2.0, 10)
    assert jts[0] == 1000 * MS and (d[:10] == 1).all() and mv[0] > 2.0
    assert len(jumps.jump_stamps(b, 5.0, 10)[0]) == 0 or jumps.jump_stamps(b, 5.0, 10)[2].min() >= 5.0


def test_after_jump_window_is_inclusive_and_5_ms():
    jts = np.array([1000 * MS], np.int64)
    t = np.array([999 * MS, 1000 * MS, 1005 * MS, 1005 * MS + 1], np.int64)
    assert jumps.after_jump(t, jts).tolist() == [False, True, True, False]


def test_stale_gone_and_thin():
    b = _book()
    t = np.array([1000 * MS] * 3, np.int64); side = np.array([1, 1, -1])
    g2, th2 = jumps.stale(b, t[:1], side[:1], 2)
    assert not g2[0] and th2[0]                       # same price, below order size
    g5, _ = jumps.stale(b, t[:1], side[:1], 5)
    assert g5[0]                                      # ask moved up, gone for a buyer
    gb, _ = jumps.stale(b, t[2:], side[2:], 5)
    assert not gb[0]                                  # bid did not fall


def test_dS_zero_on_flat_book_and_first_column_zero():
    b = _book()
    d = jumps.dS_all(b, np.array([100 * MS, 300 * MS], np.int64), np.array([1, -1]))
    assert np.allclose(d, 0.0)


def test_specs_frozen():
    assert jumps.SPECS["A"] == dict(k_bps=2.0, w_ms=10, primary=True)
    assert jumps.WINDOW_MS == 5 and jumps.STALE_H_MS == (1, 2, 5)
