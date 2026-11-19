"""Real decision to acknowledgement latency on the Alpaca paper account.

Exactly as in PREREGISTRATION.md. 200 limit buys on BTC/USD at half the best bid,
smallest quantity the venue lists, one every 3 s, each cancelled right after its
acknowledgement. Time is local monotonic from just before the request to the
response. Fills from the paper account are never used for anything.

The account secret is added by the sandbox for paper-api.alpaca.markets. The key
id is read from the environment variable ALPACA_KEY_ID and is never stored here.
"""
import json, os, statistics, sys, time
import urllib.request, urllib.error

BASE = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
N, GAP = 200, 3.0

def call(method, url, body=None, key=True):
    h = {"Content-Type": "application/json"}
    if key:
        h["APCA-API-KEY-ID"] = os.environ["ALPACA_KEY_ID"]
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read(); code = r.status
    except urllib.error.HTTPError as e:
        raw = e.read(); code = e.code
    except Exception as e:
        return None, 0, f"{type(e).__name__}: {e}", t0, time.monotonic()
    t1 = time.monotonic()
    try:
        js = json.loads(raw) if raw else None
    except Exception:
        js = raw.decode(errors="replace")[:200]
    return js, code, None, t0, t1

def pct(xs, p):
    xs = sorted(xs); k = (len(xs) - 1) * p
    lo = int(k); hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)

def main(out):
    asset, *_ = call("GET", f"{BASE}/v2/assets/BTC/USD")
    qty = asset["min_order_size"]
    rows, fails = [], 0
    start = time.monotonic()
    for i in range(N):
        due = start + i * GAP
        time.sleep(max(0, due - time.monotonic()))
        q, *_ = call("GET", f"{DATA}/v1beta3/crypto/us/latest/quotes?symbols=BTC/USD", key=False)
        bid = q["quotes"]["BTC/USD"]["bp"]
        px = round(bid / 2, 2)
        body = {"symbol": "BTC/USD", "qty": qty, "side": "buy", "type": "limit",
                "time_in_force": "gtc", "limit_price": str(px)}
        js, code, err, t0, t1 = call("POST", f"{BASE}/v2/orders", body)
        row = {"i": i, "bid": bid, "limit": px, "http": code, "err": err,
               "latency_ms": (t1 - t0) * 1000,
               "submitted_at": js.get("submitted_at") if isinstance(js, dict) else None,
               "msg": None if code == 200 else js}
        ok = code == 200 and isinstance(js, dict) and "id" in js
        if not ok:
            fails += 1
        else:
            _, ccode, cerr, c0, c1 = call("DELETE", f"{BASE}/v2/orders/{js['id']}")
            row["cancel_http"] = ccode; row["cancel_ms"] = (c1 - c0) * 1000
        row["ok"] = ok
        rows.append(row)
        print(i, code, round(row["latency_ms"], 1), flush=True)
    lat = [r["latency_ms"] for r in rows if r["ok"]]
    summ = {"orders": N, "qty": qty, "failures": fails, "acknowledged": len(lat)}
    if lat:
        summ.update(median_ms=statistics.median(lat), p90_ms=pct(lat, .9), p99_ms=pct(lat, .99),
                    min_ms=min(lat), max_ms=max(lat))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"summary": summ, "rows": rows}, open(out, "w"), indent=1)
    print(summ)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/latency/alpaca_paper_latency.json")
