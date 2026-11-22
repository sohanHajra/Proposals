"""RQ2 real order lifecycles and where cancellations land (LOBSTER, Nasdaq, 2012-06-21).

Built as written in PREREGISTRATION.md (RQ2 and the 2026-11-19 evening deviation entry),
before its first run.

Part A, H4: Orders submitted at the best price on their side (the book row of the
submission) with at least one visible execution in the file. Rest time is submission to
first visible execution in ms. Markout is dir x (mid 1 s after the first fill minus fill
price) / fill price x 1e4, so positive is good for the resting order. Controls read on the
book just before the submission: spread in ticks, log(1 + displayed size at the order's
price), top of book imbalance signed to the order's side, realised volatility of the mid
over the previous 60 s (1 s samples, bps), half hour of the day as fixed effects. OLS with
standard errors clustered by minute of submission. Run with and without controls.
H4 is judged on INTC and MSFT only.

Part B, exploratory: Every full deletion (type 3) of an order whose submission is in the
file. The queue at its price is rebuilt from the messages in time priority. A deletion is
used only when the rebuilt queue's total equals the displayed size at that price in the
book just before it and holds at least two orders. Position p = shares ahead /
(level total - own size), 0 at the front and 1 at the back. Distance of the p
distribution to each cancellation rule (Wasserstein 1): front = mean p, back = 1 - mean p,
random (uniform by quantity) = integral |F(x) - x|. Smallest is closest. Partial
cancellations (type 2) reported the same way as a second line.

Usage: python -m s2f.lobster_rq2
"""
import json
import numpy as np
import polars as pl
import statsmodels.formula.api as smf
from .paths import RAW, RESULTS

TICKERS = ["AAPL", "AMZN", "GOOG", "INTC", "MSFT"]
MAIN = ["INTC", "MSFT"]
DAY = "2012-06-21"
TICK = 100
OPEN_S = 34200.0
NBOOT = 2000
SEED = 20261115


def load(t):
    d = RAW / "lobster"
    stem = f"{t}_{DAY}_34200000_57600000"
    msg = pl.read_csv(d / f"{stem}_message_10.csv", has_header=False,
                      new_columns=["time", "type", "oid", "size", "price", "dir"])
    ob = pl.read_csv(d / f"{stem}_orderbook_10.csv", has_header=False)
    return msg, ob.to_numpy()


def level_size(row, side, price):
    """Displayed size at price on side in one orderbook row (0 if not shown)."""
    # columns: ask p, ask s, bid p, bid s, repeated for 10 levels
    off = 0 if side == -1 else 2
    prices = row[off::4]
    sizes = row[off + 1::4]
    hit = np.nonzero(prices == price)[0]
    return int(sizes[hit[0]]) if hit.size else 0, bool(hit.size)


def mids_of(ob):
    return (ob[:, 0] + ob[:, 2]) / 2.0


def sample_mid(times, mid, q):
    i = np.searchsorted(times, q, side="right") - 1
    return np.where(i >= 0, mid[np.clip(i, 0, None)], np.nan)


def part_a(t, msg, ob):
    times = msg["time"].to_numpy()
    typ = msg["type"].to_numpy()
    oid = msg["oid"].to_numpy()
    price = msg["price"].to_numpy()
    side = msg["dir"].to_numpy()
    mid = mids_of(ob)
    n = len(times)
    # first visible execution per order
    ex = msg.with_row_index("i").filter(pl.col("type") == 4).group_by("oid", maintain_order=True).agg(
        tf=pl.col("time").first(), pf=pl.col("price").first())
    ex_map = {o: (a, b) for o, a, b in ex.iter_rows()}
    rows = []
    counts = {"submissions": 0, "at_best": 0, "improved_best": 0,
              "with_visible_exec": 0, "rest_le_zero": 0, "first_minute": 0, "late_fill": 0}
    end_t = times[-1]
    for i in np.nonzero(typ == 1)[0]:
        if i == 0:
            continue
        counts["submissions"] += 1
        s = side[i]
        best_now = ob[i, 2] if s == 1 else ob[i, 0]
        if price[i] != best_now:
            continue
        counts["at_best"] += 1
        prev = ob[i - 1]
        best_before = prev[2] if s == 1 else prev[0]
        improved = price[i] != best_before
        counts["improved_best"] += int(improved)
        e = ex_map.get(oid[i])
        if e is None:
            continue
        counts["with_visible_exec"] += 1
        tf, pf = e
        rest = (tf - times[i]) * 1000.0
        if rest <= 0:
            counts["rest_le_zero"] += 1
            continue
        if times[i] < OPEN_S + 60:
            counts["first_minute"] += 1
            continue
        if tf + 1.0 > end_t:
            counts["late_fill"] += 1
            continue
        rows.append((i, s, times[i], tf, pf, rest, improved))
    if not rows:
        return counts, None
    r = np.array([x[:6] for x in rows], dtype=float)
    idx = r[:, 0].astype(int)
    s = r[:, 1]
    t0, tf, pf, rest = r[:, 2], r[:, 3], r[:, 4], r[:, 5]
    m1 = sample_mid(times, mid, tf + 1.0)
    mk = s * (m1 - pf) / pf * 1e4
    prev = ob[idx - 1]
    spread_t = (prev[:, 0] - prev[:, 2]) / TICK
    dsz = np.array([level_size(ob[k - 1], int(sd), price[k])[0] for k, sd in zip(idx, s)])
    imb = (prev[:, 3] - prev[:, 1]) / (prev[:, 3] + prev[:, 1])
    grid = t0[:, None] - np.arange(60, -1, -1)[None, :]
    mg = sample_mid(times, mid, grid.ravel()).reshape(grid.shape)
    lr = np.diff(np.log(mg), axis=1) * 1e4
    vol = np.sqrt((lr ** 2).sum(axis=1))
    df = pl.DataFrame({
        "markout_bps": mk, "log_rest": np.log(rest), "rest_ms": rest,
        "spread_ticks": spread_t, "log_size": np.log1p(dsz),
        "imb_signed": s * imb, "vol60_bps": vol,
        "halfhour": ((t0 - OPEN_S) // 1800).astype(int),
        "minute": ((t0 - OPEN_S) // 60).astype(int),
        "improved": np.array([x[6] for x in rows]),
    }).filter(pl.all_horizontal(pl.col(pl.Float64).is_finite()))
    return counts, df


def ols(df, formula):
    pdf = df.to_pandas()
    m = smf.ols(formula, data=pdf).fit(cov_type="cluster",
                                       cov_kwds={"groups": pdf["minute"]})
    b = float(m.params["log_rest"])
    lo, hi = (float(x) for x in m.conf_int().loc["log_rest"])
    return {"coef_log_rest": round(b, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "n": int(m.nobs), "clusters": int(pdf["minute"].nunique()),
            "r2": round(float(m.rsquared), 4)}


CTRL = "markout_bps ~ log_rest + spread_ticks + log_size + imb_signed + vol60_bps + C(halfhour)"
BARE = "markout_bps ~ log_rest"


def summarize_a(t, counts, df):
    out = {"counts": counts}
    if df is None or df.height < 50:
        out["note"] = "too few orders"
        return out
    out["n_used"] = df.height
    out["rest_ms_quantiles"] = {str(q): round(float(df["rest_ms"].quantile(q)), 3)
                                for q in (0.1, 0.25, 0.5, 0.75, 0.9)}
    out["markout_bps_mean"] = round(float(df["markout_bps"].mean()), 4)
    out["markout_bps_median"] = round(float(df["markout_bps"].median()), 4)
    out["spread_1tick_share_at_submission"] = round(float((df["spread_ticks"] == 1).mean()), 4)
    out["bare"] = ols(df, BARE)
    out["controls"] = ols(df, CTRL)
    # robustness, written in the spec: joined an existing best only
    j = df.filter(~pl.col("improved"))
    out["controls_joined_existing_best_only"] = ols(j, CTRL) if j.height >= 50 else None
    return out


def part_b(t, msg, ob):
    times = msg["time"].to_numpy()
    typ = msg["type"].to_numpy()
    oid = msg["oid"].to_numpy()
    size = msg["size"].to_numpy()
    price = msg["price"].to_numpy()
    side = msg["dir"].to_numpy()
    queues = {}   # (side, price) -> dict oid -> size, insertion order = time priority
    where = {}    # oid -> (side, price)
    res = {3: [], 2: []}
    cnt = {k: {"events": 0, "known_order": 0, "level_in_book": 0, "consistent": 0,
               "two_plus_orders": 0} for k in ("delete", "partial")}
    for i in range(len(times)):
        ty = typ[i]
        o = oid[i]
        if ty == 1:
            key = (int(side[i]), int(price[i]))
            queues.setdefault(key, {})[o] = int(size[i])
            where[o] = key
            continue
        if ty not in (2, 3, 4):
            continue
        if ty in (2, 3) and i > 0:
            c = cnt["delete" if ty == 3 else "partial"]
            c["events"] += 1
            if o in where:
                c["known_order"] += 1
                key = where[o]
                q = queues[key]
                disp, shown = level_size(ob[i - 1], key[0], key[1])
                if shown:
                    c["level_in_book"] += 1
                    tot = sum(q.values())
                    if tot == disp:
                        c["consistent"] += 1
                        if len(q) >= 2:
                            c["two_plus_orders"] += 1
                            ahead = 0
                            for k2, v in q.items():
                                if k2 == o:
                                    break
                                ahead += v
                            own = q[o]
                            best = ob[i - 1, 2] if key[0] == 1 else ob[i - 1, 0]
                            res[ty].append((times[i], ahead / (tot - own),
                                            int(key[1] == best), own))
        if o in where:
            key = where[o]
            q = queues[key]
            if ty == 3:
                q.pop(o, None)
                where.pop(o)
            else:
                q[o] -= int(size[i])
                if q[o] <= 0:
                    q.pop(o)
                    where.pop(o)
            if not q:
                queues.pop(key)
    return cnt, {k: np.array(v) for k, v in res.items()}


GRID = np.linspace(0.0, 1.0, 10001)


def w1_uniform(p):
    """Integral of |F_n(x) - x| over [0, 1] on a grid of 10,001 points."""
    F = np.searchsorted(np.sort(p), GRID, side="right") / p.size
    return float(np.trapezoid(np.abs(F - GRID), GRID))


def dists(p):
    return {"front": float(p.mean()), "random": w1_uniform(p), "back": float(1 - p.mean())}


def summarize_b(arr):
    if arr.size == 0 or arr.shape[0] < 50:
        return {"n": int(arr.shape[0]) if arr.size else 0, "note": "too few"}
    tt, p = arr[:, 0], arr[:, 1]
    d = dists(p)
    closest = min(d, key=d.get)
    blocks = ((tt - OPEN_S) // 300).astype(int)
    ub = np.unique(blocks)
    rng = np.random.default_rng(SEED)
    by = {b: p[blocks == b] for b in ub}
    bm, wins = [], {"front": 0, "random": 0, "back": 0}
    for _ in range(NBOOT):
        pick = rng.choice(ub, size=ub.size, replace=True)
        pp = np.concatenate([by[b] for b in pick])
        bm.append(pp.mean())
        if _ < 500:  # uniform distance is slower; closest-rule stability on 500 resamples
            dd = dists(pp)
            wins[min(dd, key=dd.get)] += 1
    lo, hi = np.percentile(bm, [2.5, 97.5])
    return {
        "n": int(p.size),
        "mean_p": round(float(p.mean()), 4), "mean_p_ci95": [round(float(lo), 4), round(float(hi), 4)],
        "median_p": round(float(np.median(p)), 4),
        "share_p_eq_0": round(float((p == 0).mean()), 4),
        "share_p_eq_1": round(float((p == 1).mean()), 4),
        "decile_shares": [round(float(x), 4) for x in
                          np.histogram(p, bins=np.linspace(0, 1, 11))[0] / p.size],
        "w1_distance": {k: round(v, 4) for k, v in d.items()},
        "closest_rule": closest,
        "closest_rule_share_of_500_resamples": {k: v / 500 for k, v in wins.items()},
    }


def run():
    out = {"day": DAY, "label": "Nasdaq 2012-06-21 only, one day, not evidence about Binance",
           "h4_main": MAIN, "rq2": {}, "cancel_position": {}}
    for t in TICKERS:
        msg, ob = load(t)
        c, df = part_a(t, msg, ob)
        out["rq2"][t] = summarize_a(t, c, df)
        cnt, res = part_b(t, msg, ob)
        cb = {"counts": cnt}
        for ty, name in ((3, "delete"), (2, "partial")):
            a = res[ty]
            cb[name + "_all_levels"] = summarize_b(a)
            cb[name + "_at_best"] = summarize_b(a[a[:, 2] == 1] if a.size else a)
        out["cancel_position"][t] = cb
        print(t, "done", flush=True)
    h = {}
    for t in MAIN:
        r = out["rq2"][t].get("controls")
        h[t] = bool(r and r["ci95"][1] < 0)
    out["H4_supported"] = all(h.values())
    out["H4_by_ticker_ci_below_zero"] = h
    RESULTS.joinpath("lobster").mkdir(parents=True, exist_ok=True)
    (RESULTS / "lobster" / f"rq2_{DAY}.json").write_text(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
