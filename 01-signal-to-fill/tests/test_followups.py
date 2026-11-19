import numpy as np
from s2f.replay import Book
from s2f.signals import first_per_gap, last_row_per_stamp, imbalance, make_signal_decisions
from s2f.stats import group_diff, group_mean, contribution
from s2f.taker_followups import realised_vol_bps, walk_px
from s2f import passive

US = 10**6


def test_first_per_gap_keeps_one_per_second():
    ts = np.array([0, 10, 999_999, 1_000_000, 1_500_000, 2_100_000])
    assert first_per_gap(ts).tolist() == [0, 3, 5]


def test_last_row_per_stamp():
    assert last_row_per_stamp(np.array([5, 5, 6, 7, 7, 7])).tolist() == [1, 2, 5]


def test_imbalance_sign_and_zero_size():
    assert imbalance(np.array([3.0, 0.0]), np.array([1.0, 0.0])).tolist() == [0.5, 0.0]


def _book(n=4000):
    ts = np.arange(n, dtype=np.int64) * 500_000          # one row every 0.5 s
    bid = np.full(n, 100.0); ask = np.full(n, 100.1)
    bq = np.ones(n); aq = np.ones(n)
    bq[::7] = 99.0                                        # strong bid imbalance on some rows
    return Book(ts, bid, bq.astype(np.float32), ask, aq.astype(np.float32))


def test_signal_decisions_side_and_spacing():
    b = _book()
    t, side, ngaps, thr = make_signal_decisions(b, thr=0.9)
    assert ngaps == 0 and (side == 1).all()
    assert (np.diff(t) >= US).all()
    assert t.max() < b.ts[-1] - 600 * US


def test_group_diff_and_contribution():
    rng = np.random.default_rng(0)
    t = np.sort(rng.integers(0, 3600 * US, 4000))
    g = rng.random(4000) < 0.3
    v = np.where(g, 2.0, 0.0) + rng.normal(0, 0.1, 4000)
    r = group_diff(v, g, t)
    assert abs(r["diff"] - 2.0) < 0.05 and r["ci95"][0] < r["diff"] < r["ci95"][1]
    parts = [contribution(v, m, t)["contribution"] for m in (g, ~g)]
    assert abs(sum(parts) - v.mean()) < 1e-12
    assert abs(group_mean(v, g, t)["mean"] - v[g].mean()) < 1e-12


def test_realised_vol_zero_on_flat_mid():
    b = _book()
    assert np.allclose(realised_vol_bps(b, np.array([100 * US, 500 * US])), 0.0)


def _snaps(side_px, side_q, ts):
    return dict(snap_ts=np.array(ts, np.int64), snap_px=np.array(side_px, float), snap_q=np.array(side_q, float))


def test_walk_goes_past_a_thin_touch():
    ts = np.array([0, 1000], np.int64)
    b = Book(ts, np.array([99.9, 99.9]), np.array([1, 1], np.float32), np.array([100.0, 100.0]),
             np.array([0.004, 0.004], np.float32))
    S = {1: _snaps([[99.9, 99.8, 99.7, 99.6, 99.5]], [[1] * 5], [0]),
         -1: _snaps([[-100.0, -100.1, -100.2, -100.3, -100.4]], [[0.004, 0.003, 1, 1, 1]], [0])}
    px, flag = walk_px(b, S, np.array([1000]), np.array([1]))
    assert np.isclose(px[0], (0.004 * 100.0 + 0.003 * 100.1 + 0.003 * 100.2) / 0.01) and not flag[0]


def test_passive_tie_flip_replays_events_on_the_arrival_stamp():
    ts = np.array([1000, 2000], np.int64)
    b = Book(ts, np.array([100.0, 100.0]), np.array([0.005, 0.005], np.float32),
             np.array([100.1, 100.1]), np.array([1, 1], np.float32))
    S = {1: dict(tick_ts=ts, tick_px=np.array([100.0, 100.0]), tick_q=np.array([0.005, 0.005]),
                 tr_ts=np.array([2000], np.int64), tr_px=np.array([100.0]), tr_q=np.array([0.02]),
                 snap_ts=np.array([1000], np.int64), snap_px=np.array([[100.0, 99.9, 99.8, 99.7, 99.6]]),
                 snap_q=np.ones((1, 5)))}
    after = passive.one(b, S, 1000, 1, 1000, 1, tie_after=True)
    before = passive.one(b, S, 1000, 1, 1000, 1, tie_after=False)
    assert (after["filled"] == 0).all()
    assert np.allclose(before["filled"], 0.01)
