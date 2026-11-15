"""Audit the LOBSTER sample files (Nasdaq, 2012-06-21, 10 levels).

Caveat: the files only carry messages inside the 10 level window, so an
order that leaves the window can look open at the close.
Checks what RQ2 needs: message types, timestamp resolution, crossed books,
spread in ticks, and how many order lifecycles are complete inside the file
(submitted in the file and ended by an execution or a full delete).
Usage: python -m s2f.lobster_audit
"""
import json
import polars as pl
from .paths import RAW, RESULTS

TICKERS = ["AAPL", "AMZN", "GOOG", "INTC", "MSFT"]
DAY = "2012-06-21"
TICK = 100  # one cent in LOBSTER price units (dollars x 10000)
DUMMY = 9999999999


def _files(t):
    d = RAW / "lobster"
    stem = f"{t}_{DAY}_34200000_57600000"
    return d / f"{stem}_message_10.csv", d / f"{stem}_orderbook_10.csv"


def audit_one(t: str) -> dict:
    mf, of = _files(t)
    msg = pl.read_csv(mf, has_header=False,
                      new_columns=["time", "type", "oid", "size", "price", "dir"])
    ob = pl.read_csv(of, has_header=False, columns=[0, 1, 2, 3])
    ob.columns = ["ap1", "as1", "bp1", "bs1"]
    out = {"ticker": t, "day": DAY, "message_rows": msg.height,
           "orderbook_rows": ob.height}
    out["rows_match"] = msg.height == ob.height
    out["type_counts"] = {str(k): int(v) for k, v in
                          msg.group_by("type").len().sort("type").iter_rows()}
    out["time_first_last_s"] = [float(msg["time"][0]), float(msg["time"][-1])]
    out["nonmonotone_time"] = int((msg["time"].diff().drop_nulls() < 0).sum())
    # timestamp resolution: smallest positive gap between messages
    gaps = msg["time"].diff().drop_nulls()
    pos = gaps.filter(gaps > 0)
    out["min_positive_gap_ns"] = round(float(pos.min()) * 1e9, 1)
    out["share_messages_same_time_as_previous"] = round(float((gaps == 0).mean()), 4)
    valid = ob.filter((ob["ap1"] < DUMMY) & (ob["bp1"] > -DUMMY))
    out["rows_one_side_empty"] = ob.height - valid.height
    spread_t = ((valid["ap1"] - valid["bp1"]) / TICK).round(0)
    out["crossed_or_locked_rows"] = int((spread_t <= 0).sum())
    out["spread_1tick_share"] = round(float((spread_t == 1).mean()), 4)
    out["spread_ticks_median_p99"] = [float(spread_t.quantile(0.5)), float(spread_t.quantile(0.99))]
    mid = (valid["ap1"] + valid["bp1"]) / 2 / 10000
    out["mid_median_usd"] = round(float(mid.median()), 3)
    out["tick_bps_at_median_mid"] = round(0.01 / float(mid.median()) * 1e4, 3)

    # order lifecycles (orders with id 0 or hidden executions have no lifecycle)
    sub = msg.filter(pl.col("type") == 1).select("oid", t0="time", s0="size")
    ends = (msg.filter(pl.col("type").is_in([3, 4]))
            .group_by("oid").agg(t1=pl.col("time").max(),
                                 n_exec=(pl.col("type") == 4).sum(),
                                 n_del=(pl.col("type") == 3).sum()))
    ids_in_file = msg.filter(pl.col("type").is_in([2, 3, 4]))["oid"].unique()
    out["orders_submitted_in_file"] = sub.height
    submitted = set(sub["oid"].to_list())
    out["orders_acted_on_without_submission_in_file"] = sum(
        1 for o in ids_in_file.to_list() if o not in submitted)
    life = sub.join(ends, on="oid", how="left")
    done = life.filter(pl.col("t1").is_not_null())
    out["submitted_with_end_in_file"] = done.height
    out["submitted_still_open_at_close"] = life.height - done.height
    out["ended_with_any_visible_execution"] = int((done["n_exec"] > 0).sum())
    out["ended_by_delete_without_execution"] = int(((done["n_exec"] == 0) & (done["n_del"] > 0)).sum())
    out["share_of_ended_with_any_visible_execution"] = round(
        out["ended_with_any_visible_execution"] / max(done.height, 1), 4)
    lt = (done["t1"] - done["t0"]) * 1000  # ms
    out["lifetime_ms_quantiles"] = {str(q): round(float(lt.quantile(q)), 3)
                                    for q in [0.1, 0.25, 0.5, 0.75, 0.9]}
    dele = done.filter((pl.col("n_exec") == 0) & (pl.col("n_del") > 0))
    lt_d = (dele["t1"] - dele["t0"]) * 1000
    out["deleted_without_fill_share_within_100ms"] = round(float((lt_d <= 100).mean()), 4)
    out["hidden_execution_rows"] = out["type_counts"].get("5", 0)
    out["halt_rows"] = out["type_counts"].get("7", 0)
    return out


if __name__ == "__main__":
    res = {t: audit_one(t) for t in TICKERS}
    RESULTS.joinpath("audit").mkdir(parents=True, exist_ok=True)
    (RESULTS / "audit" / f"lobster_{DAY}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
