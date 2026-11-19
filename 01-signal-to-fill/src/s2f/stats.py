"""Block bootstrap helpers shared by the follow up analyses.

Every interval resamples whole 5 minute blocks of decision time with replacement, 2,000 times,
seed 20261115, and reports the 2.5th and 97.5th percentiles, as in the preregistration.
Group statistics are ratios of block sums inside each resample, so a block keeps all its decisions
together whichever group they fall in. Cells that are not finite (no fill, no markout) are left out.
"""
import numpy as np

from .taker import SEED, BLOCK_US

NBOOT = 2000


def _blocks(t):
    blk = ((t - t.min()) // BLOCK_US).astype(int)
    ub, inv = np.unique(blk, return_inverse=True)
    return inv, len(ub)


def _idx(nb, nboot=NBOOT, seed=SEED):
    return np.random.default_rng(seed).integers(0, nb, (nboot, nb))


def _ci(b):
    b = b[np.isfinite(b)]
    if len(b) == 0:
        return [None, None]
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def group_mean(v, mask, t, nboot=NBOOT, seed=SEED):
    """Mean of v over decisions where mask holds and v is finite, with its interval."""
    m = mask & np.isfinite(v)
    inv, nb = _blocks(t)
    s = np.bincount(inv, np.where(m, v, 0.0), minlength=nb); c = np.bincount(inv, m * 1.0, minlength=nb)
    if c.sum() == 0:
        return dict(mean=None, ci95=[None, None], n=0)
    bi = _idx(nb, nboot, seed)
    with np.errstate(invalid="ignore", divide="ignore"):
        b = s[bi].sum(1) / c[bi].sum(1)
    return dict(mean=float(s.sum() / c.sum()), ci95=_ci(b), n=int(c.sum()))


def group_diff(v, g, t, nboot=NBOOT, seed=SEED):
    """Mean of v where g holds minus mean of v where g does not, with its interval."""
    f = np.isfinite(v)
    a = g & f; r = ~g & f
    inv, nb = _blocks(t)
    sa = np.bincount(inv, np.where(a, v, 0.0), minlength=nb); ca = np.bincount(inv, a * 1.0, minlength=nb)
    sr = np.bincount(inv, np.where(r, v, 0.0), minlength=nb); cr = np.bincount(inv, r * 1.0, minlength=nb)
    if ca.sum() == 0 or cr.sum() == 0:
        return dict(diff=None, ci95=[None, None], n_group=int(ca.sum()), n_rest=int(cr.sum()))
    bi = _idx(nb, nboot, seed)
    with np.errstate(invalid="ignore", divide="ignore"):
        b = sa[bi].sum(1) / ca[bi].sum(1) - sr[bi].sum(1) / cr[bi].sum(1)
    return dict(diff=float(sa.sum() / ca.sum() - sr.sum() / cr.sum()), ci95=_ci(b),
                mean_group=float(sa.sum() / ca.sum()), mean_rest=float(sr.sum() / cr.sum()),
                n_group=int(ca.sum()), n_rest=int(cr.sum()))


def contribution(v, mask, t, nboot=NBOOT, seed=SEED):
    """Sum of v over the mask divided by the number of all decisions with finite v.
    Contributions of a partition add up to the overall mean."""
    f = np.isfinite(v)
    m = mask & f
    inv, nb = _blocks(t)
    s = np.bincount(inv, np.where(m, v, 0.0), minlength=nb); c = np.bincount(inv, f * 1.0, minlength=nb)
    bi = _idx(nb, nboot, seed)
    b = s[bi].sum(1) / c[bi].sum(1)
    return dict(contribution=float(s.sum() / c.sum()), ci95=_ci(b), n=int(m.sum()))


def unmatched_diff(a1, a5, t, nboot=NBOOT, seed=SEED):
    """Mean of a5 over its finite cells minus mean of a1 over its finite cells. The two sets of
    decisions differ, so this is the conditional comparison the preregistration warns about."""
    f1 = np.isfinite(a1); f5 = np.isfinite(a5)
    inv, nb = _blocks(t)
    s1 = np.bincount(inv, np.where(f1, a1, 0.0), minlength=nb); c1 = np.bincount(inv, f1 * 1.0, minlength=nb)
    s5 = np.bincount(inv, np.where(f5, a5, 0.0), minlength=nb); c5 = np.bincount(inv, f5 * 1.0, minlength=nb)
    bi = _idx(nb, nboot, seed)
    with np.errstate(invalid="ignore", divide="ignore"):
        b = s5[bi].sum(1) / c5[bi].sum(1) - s1[bi].sum(1) / c1[bi].sum(1)
    return dict(diff=float(s5.sum() / c5.sum() - s1.sum() / c1.sum()), ci95=_ci(b),
                n_1ms=int(c1.sum()), n_500ms=int(c5.sum()))
