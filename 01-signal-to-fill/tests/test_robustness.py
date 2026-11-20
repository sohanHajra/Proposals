import numpy as np
from s2f.replay import Book
from s2f import passive, robustness, taker

US = 10**6


def _one_level_book():
    ts = np.array([1000, 2000], np.int64)
    b = Book(ts, np.array([100.0, 100.0]), np.array([0.005, 0.005], np.float32),
             np.array([100.1, 100.1]), np.array([1, 1], np.float32))
    S = {1: dict(tick_ts=ts, tick_px=np.array([100.0, 100.0]), tick_q=np.array([0.005, 0.005]),
                 tr_ts=np.array([3000, 5 * US], np.int64), tr_px=np.array([100.0, 100.0]),
                 tr_q=np.array([0.01, 2.0]),
                 snap_ts=np.array([1000], np.int64), snap_px=np.array([[100.0, 99.9, 99.8, 99.7, 99.6]]),
                 snap_q=np.ones((1, 5)))}
    return b, S


def test_passive_defaults_unchanged_and_size_and_horizon_bite():
    b, S = _one_level_book()
    base = passive.one(b, S, 1000, 1, 1000, 1)
    same = passive.one(b, S, 1000, 1, 1000, 1, qty=passive.QTY, h_us=passive.H_US)
    assert np.allclose(base["filled"], same["filled"]) and np.allclose(base["filled"], 0.01)
    big = passive.one(b, S, 1000, 1, 1000, 1, qty=1.0)          # 0.005 ahead, then 0.005 and 2.0 trade
    assert np.allclose(big["filled"], 1.0)
    short = passive.one(b, S, 1000, 1, 1000, 1, qty=1.0, h_us=1 * US)   # the 2.0 trade at 5 s is outside 1 s
    assert np.allclose(short["filled"], 0.005)


def test_fee_shift_leaves_latency_cost_and_slope_unchanged():
    rng = np.random.default_rng(0)
    t = np.sort(rng.integers(0, 3600 * US, 500)).astype(np.int64)
    S = rng.normal(0, 1, (500, len(taker.DELAYS_MS)))
    a = robustness.h1_line(S - S[:, [0]], S, t)
    Sf = S + robustness.FEES["taker_bps"]
    f = robustness.h1_line(Sf - Sf[:, [0]], Sf, t)
    assert np.isclose(a["slope_bps_per_logms"]["est"], f["slope_bps_per_logms"]["est"], atol=1e-12)
    assert np.allclose(a["slope_bps_per_logms"]["ci95"], f["slope_bps_per_logms"]["ci95"], atol=1e-12)
    assert np.isclose(f["mean_S_by_delay_ms"][1] - a["mean_S_by_delay_ms"][1], 5.0)


def test_15_minute_blocks_change_only_the_interval():
    rng = np.random.default_rng(1)
    t = np.sort(rng.integers(0, 6 * 3600 * US, 2000)).astype(np.int64)
    dS = rng.normal(0, 1, (2000, len(taker.DELAYS_MS)))
    e5, c5 = taker.slope_blocks(dS, t)
    e15, c15 = taker.slope_blocks(dS, t, block_us=robustness.BLOCK15_US)
    assert e5 == e15 and c5 != c15


def test_fees_are_the_base_tier_as_read():
    assert robustness.FEES["maker_bps"] == 2.0 and robustness.FEES["taker_bps"] == 5.0
