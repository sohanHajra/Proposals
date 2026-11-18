import numpy as np
from s2f.passive import walk, T_TRADE, T_TICK, T_SNAP

Z5 = np.zeros(5)


def go(p, ahead, evs):
    k = np.array([e[0] for e in evs]); a = np.array([e[1] for e in evs], float); b = np.array([e[2] for e in evs], float)
    sp = np.zeros((len(evs), 5)); sq = np.zeros((len(evs), 5))
    return walk(p, ahead, k, a, b, sp, sq, np.random.default_rng(1), qty=0.01)


def test_trade_at_my_price_eats_queue_then_fills():
    f, _, _ = go(100, 1.0, [(T_TRADE, 100, 0.6), (T_TRADE, 100, 0.4), (T_TRADE, 100, 0.01)])
    assert (f == 0.01).all()


def test_trade_through_fills_all_rules():
    f, _, _ = go(100, 5.0, [(T_TRADE, 99, 0.001)])
    assert (f == 0.01).all()


def test_cancel_front_helps_back_does_not():
    # queue 1.0 ahead, someone adds 1.0 behind, then 1.0 is cancelled, then trade of 0.5 and 0.01
    evs = [(T_TICK, 100, 2.0), (T_TICK, 100, 1.0), (T_TRADE, 100, 0.5), (T_TRADE, 100, 0.01)]
    f, _, _ = go(100, 1.0, evs)
    assert f[0] == 0.01          # front rule removes the quantity ahead, trade of 0.5 clears the rest
    assert f[2] == 0.0           # back rule removes the one behind me, 0.5 still ahead


def test_ordering_front_at_least_back():
    rng = np.random.default_rng(3)
    for _ in range(50):
        evs = []
        q = 3.0
        for _ in range(30):
            if rng.random() < .5:
                q = max(0.0, q + rng.normal(0, 1)); evs.append((T_TICK, 100, q))
            else:
                evs.append((T_TRADE, 100, 0.2))
        f, _, _ = go(100, 3.0, evs)
        assert f[0] >= f[2]


def test_better_price_then_snapshot_tracks_level():
    k = np.array([T_TICK, T_SNAP, T_TRADE]); a = np.array([101.0, 0, 100.0]); b = np.array([1.0, 0, 5.0])
    sp = np.zeros((3, 5)); sq = np.zeros((3, 5)); sp[1] = [101, 100, 99, 98, 97]; sq[1] = [1, 0.5, 1, 1, 1]
    f, _, lost = walk(100, 2.0, k, a, b, sp, sq, np.random.default_rng(1))
    assert lost == -1 and (f == 0.01).all()   # snapshot shows 0.5 left at my price, a trade of 5 clears it
    f2, _, lost2 = go(100, 1.0, [(T_TICK, 101, 1.0)])
