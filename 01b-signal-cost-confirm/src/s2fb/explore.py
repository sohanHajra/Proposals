"""Exploratory follow ups written after release. Nothing here feeds the verdict.

c2_lose_race (rule written 2026-11-26, before it ran on any test day)
  C2 keeps only decisions that are never marketable on arrival, which picks orders by where the
  price goes next. Here every random decision is kept. A cell that arrives marketable is treated as
  if a faster trader took the stale price: no fill at arrival, and the order crosses at the far touch
  10 s after arrival, the same cross price the replay uses for anything left unfilled. Every other
  cell keeps its stored cost. Slope on log d with the 01 block bootstrap, under each rule.
  Read next to C2 (picks orders) and 01's H5 (keeps the free option). Not a formal bound.
"""
import numpy as np

from s2f.replay import book_index_at
from s2f.passive import RULES, H_US
from s2f.taker import DELAYS_MS, slope_blocks
from s2f.fixed_price import STATES

MK = STATES.index("marketable")


def c2_lose_race(r, book):
    t, side, state, cost = r["t"], r["side"], r["state"], r["cost"]
    k0 = [book_index_at(book, x, True) for x in t]
    mid0 = np.array([0.5 * (book.bid_px[k] + book.ask_px[k]) for k in k0])
    lose = cost.copy()
    ii, jj = np.where(state == MK)
    for i, j in zip(ii, jj):
        kx = book_index_at(book, t[i] + int(DELAYS_MS[j]) * 1000 + H_US, True)
        cross = book.ask_px[kx] if side[i] > 0 else book.bid_px[kx]
        lose[i, j, :] = side[i] * (cross - mid0[i]) / mid0[i] * 1e4
    out = dict(n_decisions=int(len(t)), marketable_cells=int(len(ii)),
               marketable_share_by_delay={int(d): float((state[:, j] == MK).mean()) for j, d in enumerate(DELAYS_MS)},
               other_cells_unchanged=bool(np.allclose(lose[state != MK], cost[state != MK], equal_nan=True)))
    for q, nm in enumerate(RULES):
        C = lose[:, :, q]
        b, ci = slope_blocks(C, t)
        out[nm] = dict(slope_bps_per_logms=dict(est=b, ci95=ci),
                       cost_by_delay={int(d): float(C[:, j].mean()) for j, d in enumerate(DELAYS_MS)})
    return out
