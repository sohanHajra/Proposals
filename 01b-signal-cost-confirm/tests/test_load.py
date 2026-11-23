"""Slow. The 01.b loader on Tardis BTCUSDT 2026-09-01 gives exactly what 01's prep_day gives."""
import numpy as np
import pytest


@pytest.mark.slow
def test_tardis_prep_matches_01():
    from s2fb import load
    from s2f.passive import prep_day
    b1, t1, S1 = load.prep("tardis", "2026-09-01", "BTCUSDT")
    b0, t0, S0 = prep_day("2026-09-01")
    for f in ("ts", "bid_px", "bid_qty", "ask_px", "ask_qty"):
        a, b = getattr(b1, f), getattr(b0, f)
        assert a.dtype == b.dtype and np.array_equal(a, b)
    for f in ("ts", "side", "px", "qty"):
        assert np.array_equal(getattr(t1, f), getattr(t0, f))
    for s in (1, -1):
        for k in S0[s]:
            assert np.array_equal(S1[s][k], S0[s][k]), k


@pytest.mark.slow
def test_parquet_reader_matches_polars_path():
    """The lean column reader gives the same arrays as reading whole frames with polars."""
    from s2fb import load
    a = load.prep("cryptostruct", "2026-09-01")
    b = load._prep_frames(*load.frames("cryptostruct", "2026-09-01", "BTCUSDT"))
    for f in ("ts", "bid_px", "bid_qty", "ask_px", "ask_qty"):
        x, y = getattr(a[0], f), getattr(b[0], f)
        assert x.dtype == y.dtype and np.array_equal(x, y)
    for f in ("ts", "side", "px", "qty"):
        assert np.array_equal(getattr(a[1], f), getattr(b[1], f))
    for s in (1, -1):
        for k in a[2][s]:
            assert a[2][s][k].dtype == b[2][s][k].dtype and np.array_equal(a[2][s][k], b[2][s][k]), k
