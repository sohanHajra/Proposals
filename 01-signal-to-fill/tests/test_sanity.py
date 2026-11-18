import numpy as np
from s2f.replay import Book, Trades
from s2f.sanity import sanity
from s2f.tie_share import tie_share


def test_sanity_uses_strictly_earlier_book():
    b = Book(np.array([1000, 2000, 3000]), np.array([99.0, 100.0, 101.0]), np.ones(3, np.float32),
             np.array([100.0, 101.0, 102.0]), np.ones(3, np.float32))
    # a buy at 2000 printing 100 matches the ask shown at 1000, not the update stamped at 2000
    tr = Trades(np.array([2000, 3500]), np.array([1, -1]), np.array([100.0, 101.0]), np.ones(2))
    r = sanity(b, tr)
    assert r["buy_trade_px_equals_prior_ask"] == 1.0
    assert r["buy_trade_px_equals_ask_incl_same_ts_update"] == 0.0
    assert r["sell_trade_px_equals_prior_bid"] == 1.0


def test_tie_share_only_on_exact_stamps():
    ts = np.arange(0, 10_000_000, 1000, dtype=np.int64)
    H = tie_share(ts, np.array([5000, 5500]))
    assert H[0].all() and not H[1].any()
