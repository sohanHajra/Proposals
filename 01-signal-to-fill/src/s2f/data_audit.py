"""Audit one Tardis day: row counts, feed latency, crossed books, gaps, spreads."""
import json, sys
import polars as pl
from .paths import RAW, RESULTS

TICK = 0.1

def audit(day: str, symbol: str = "BTCUSDT") -> dict:
    d = RAW / "tardis"
    bt = pl.read_csv(d / f"binance-futures_book_ticker_{day}_{symbol}.csv.gz",
                     columns=["timestamp", "local_timestamp", "ask_amount", "ask_price", "bid_price", "bid_amount"])
    tr = pl.read_csv(d / f"binance-futures_trades_{day}_{symbol}.csv.gz",
                     columns=["timestamp", "local_timestamp", "side", "price", "amount"])
    out = {"day": day, "symbol": symbol}
    lat_bt = (bt["local_timestamp"] - bt["timestamp"]) / 1000.0  # ms
    lat_tr = (tr["local_timestamp"] - tr["timestamp"]) / 1000.0
    q = [0.01, 0.5, 0.9, 0.99, 0.999]
    out["book_ticker_rows"] = bt.height
    out["trade_rows"] = tr.height
    out["exchange_ts_all_whole_ms_bt"] = bool((bt["timestamp"] % 1000 == 0).all())
    out["feed_latency_ms_bt_quantiles"] = {str(k): round(float(lat_bt.quantile(k)), 3) for k in q}
    out["feed_latency_ms_trades_quantiles"] = {str(k): round(float(lat_tr.quantile(k)), 3) for k in q}
    out["negative_feed_latency_rows_bt"] = int((lat_bt < 0).sum())
    spread_ticks = ((bt["ask_price"] - bt["bid_price"]) / TICK).round(0)
    out["crossed_or_locked_rows"] = int((spread_ticks <= 0).sum())
    out["spread_1tick_share"] = round(float((spread_ticks == 1).mean()), 6)
    out["spread_ticks_quantiles"] = {str(k): float(spread_ticks.quantile(k)) for k in q}
    ts = bt["local_timestamp"].sort()
    gaps = ts.diff().drop_nulls() / 1e6
    out["max_gap_s_bt_local"] = round(float(gaps.max()), 3)
    out["gaps_over_1s_bt"] = int((gaps > 1).sum())
    out["nonmonotone_exchange_ts_bt"] = int((bt["timestamp"].diff().drop_nulls() < 0).sum())
    out["trade_volume_btc"] = round(float(tr["amount"].sum()), 3)
    out["trade_buy_share"] = round(float((tr["side"] == "buy").mean()), 4)
    mid = (bt["ask_price"] + bt["bid_price"]) / 2
    out["mid_open_close"] = [float(mid[0]), float(mid[-1])]
    out["mid_min_max"] = [float(mid.min()), float(mid.max())]
    return out

if __name__ == "__main__":
    day = sys.argv[1]
    res = audit(day)
    RESULTS.joinpath("audit").mkdir(parents=True, exist_ok=True)
    (RESULTS / "audit" / f"tardis_{day}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
