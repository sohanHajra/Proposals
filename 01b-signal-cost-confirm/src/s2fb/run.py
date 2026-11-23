"""The 01.b runner. One listed day, one unit at a time, each unit once.

Usage
  python -m s2fb.run SOURCE SYM DAY next     run the next unit of that day
  python -m s2fb.run SOURCE SYM DAY status   list the units and which are done

SOURCE is cryptostruct, tardis or bybit. Only the days in s2fb.days are accepted, plus 2026-09-01
for building. Every unit writes its own file under results/ROLE/SOURCE_SYM_DAY/ and refuses to start
if that file is already there, so nothing is rerun. Units run in a fixed order, each in its own
process, because the machine I run on stops any job after 20 minutes.

  convert_tt   CryptoStruct top of book and trades to parquet
  convert_depth  CryptoStruct five levels from the depth stream
  convert      Bybit book and trades to parquet (Tardis needs none)
  audit        checks and the gap rule decision. A day the rule leaves out stops here
  threshold    ETHUSDT on 2026-09-01 only. The ETHUSDT threshold and size, stored once
  c1           C1 with the drift and arrival split, race sensitivity and secondary checks
  c2_after     fixed price replay, random decisions, primary tie rule (arrays kept in data/derived)
  c2_before    the same with the other tie rule
  c2           C2 and its secondary checks from the two replays

ETHUSDT days are refused until every BTCUSDT test day has finished or been left out by the gap rule.
Any day other than 2026-09-01 is refused if the 01 code differs from tag v0.1-signal-to-fill.
"""
import json
import resource
import subprocess
import sys
import time

import numpy as np

from .paths import RESULTS, DERIVED, REPO, S2F_TAG
from .days import BUILD_DAY, TEST_DAYS
from .guard import check_day_allowed, Refused

QTY_BTC = 0.01
TICK = {"BTCUSDT": 0.1, "ETHUSDT": 0.01}
ETH_FILE = RESULTS / "eth" / "threshold_ETHUSDT_2026-09-01.json"


def units(source, sym, day):
    u = []
    if source == "cryptostruct":
        u += ["convert_tt", "convert_depth"]
    elif source == "bybit":
        u.append("convert")
    u.append("audit")
    if sym == "ETHUSDT" and day == BUILD_DAY:
        u.append("threshold")
    u += ["c1", "c2_after", "c2_before", "c2"]
    return u


def folder(source, sym, day, role):
    return RESULTS / role / f"{source}_{sym}_{day}"


def unit_file(source, sym, day, role, unit):
    return folder(source, sym, day, role) / f"{unit}.json"


def array_file(source, sym, day, unit):
    return DERIVED / "c2" / f"{source}_{sym}_{day}_{unit}.npz"


def s2f_unchanged():
    r = subprocess.run(["git", "diff", "--quiet", S2F_TAG, "--", "01-signal-to-fill/src"], cwd=REPO)
    return r.returncode == 0


def btc_tests_done():
    """Each BTCUSDT test day has its last unit written, or its audit left it out."""
    missing = []
    for d in TEST_DAYS:
        if unit_file("cryptostruct", "BTCUSDT", d, "test", "c2").exists():
            continue
        a = unit_file("cryptostruct", "BTCUSDT", d, "test", "audit")
        if a.exists() and json.loads(a.read_text())["gap_rule"]["left_out"]:
            continue
        missing.append(d)
    return missing


def threshold_and_size(sym):
    """(threshold, order size) for the symbol. BTCUSDT on any venue uses the frozen 01 value."""
    from s2f.signals import frozen_threshold
    if sym == "BTCUSDT":
        return frozen_threshold(), QTY_BTC
    if not ETH_FILE.exists():
        raise Refused("the ETHUSDT threshold has not been stored yet (tardis ETHUSDT 2026-09-01, unit threshold)")
    d = json.loads(ETH_FILE.read_text())
    return d["threshold_abs_imbalance"], d["order_size_eth"]


def state(source, sym, day):
    role = check_day_allowed(day, sym, source)
    us = units(source, sym, day)
    done = [u for u in us if unit_file(source, sym, day, role, u).exists()]
    return role, us, done


def run_next(source, sym, day):
    role, us, done = state(source, sym, day)
    if day != BUILD_DAY and not s2f_unchanged():
        raise Refused(f"the 01 code differs from {S2F_TAG}")
    if sym == "ETHUSDT" and day != BUILD_DAY:
        miss = btc_tests_done()
        if miss:
            raise Refused(f"ETHUSDT waits until every BTCUSDT test day has run. Not yet: {miss}")
    a = unit_file(source, sym, day, role, "audit")
    if a.exists() and json.loads(a.read_text())["gap_rule"]["left_out"]:
        raise Refused(f"{day} was left out by the gap rule, see {a}")
    todo = [u for u in us if u not in done]
    if not todo:
        raise Refused(f"every unit of {source} {sym} {day} has run")
    if done != us[:len(done)]:
        raise Refused(f"units done out of order: {done}")
    unit = todo[0]
    out = unit_file(source, sym, day, role, unit)
    t0 = time.time()
    res = do_unit(source, sym, day, unit)
    res = {**res, **dict(unit=unit, source=source, symbol=sym, day=day, role=role, seconds=round(time.time() - t0, 1),
                        peak_memory_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))}
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise Refused(f"{out} appeared during the run, not overwriting it")
    out.write_text(json.dumps(res, indent=1, default=float))
    print("wrote", out, flush=True)
    return res


def do_unit(source, sym, day, unit):
    from . import load, analysis, audit
    if unit == "convert_tt":
        from . import cryptostruct as cs
        return dict(meta={k: v for k, v in cs.convert_tt(day, sym).items() if k != "header"})
    if unit == "convert_depth":
        from . import cryptostruct as cs
        return dict(meta=cs.convert_depth(day, sym))
    if unit == "convert":
        from . import bybit
        return dict(meta=bybit.convert(day, sym))
    if unit == "audit":
        return audit.audit(source, day, sym, TICK[sym])
    if unit == "threshold":
        return store_eth_threshold()
    thr, qty = threshold_and_size(sym)
    if unit == "c2":
        ra = dict(np.load(array_file(source, sym, day, "c2_after")))
        rb = dict(np.load(array_file(source, sym, day, "c2_before")))
        return dict(order_size=qty, C2=analysis.c2(ra, rb))
    prepped = load.prep(source, day, sym)
    book = prepped[0]
    if unit == "c1":
        t, side, ngaps = analysis.signal_decisions(book, thr)
        return dict(threshold_abs_imbalance=thr, feed_gaps_over_1s=int(ngaps), C1=analysis.c1(book, prepped[2], t, side, qty))
    if unit in ("c2_after", "c2_before"):
        f = array_file(source, sym, day, unit)
        if f.exists():
            raise Refused(f"{f} exists, not overwriting it")
        r = analysis.c2_replay(prepped, unit == "c2_after", qty)
        f.parent.mkdir(parents=True, exist_ok=True)
        np.savez(f, **r)
        return dict(arrays=f.name, n_decisions=int(len(r["t"])), feed_gaps_over_1s=int(r["ngaps"]), order_size=qty)
    raise ValueError(unit)


def store_eth_threshold():
    """ETHUSDT threshold (90th percentile of |I| on the last top of book row per stamp, as in 01)
    and size (Deviation of 2026-11-23, item 5), from 2026-09-01 only, stored once."""
    from . import load
    from s2f.signals import threshold
    if ETH_FILE.exists():
        raise Refused(f"{ETH_FILE} exists. The ETHUSDT threshold is computed once")
    eb = load.prep("tardis", BUILD_DAY, "ETHUSDT")[0]
    bb = load.prep("tardis", BUILD_DAY, "BTCUSDT")[0]
    thr = threshold(eb)
    m_btc = float(np.median(0.5 * (bb.bid_px + bb.ask_px)))
    m_eth = float(np.median(0.5 * (eb.bid_px + eb.ask_px)))
    size = round(QTY_BTC * m_btc / m_eth / 0.001) * 0.001
    d = dict(day=BUILD_DAY, threshold_abs_imbalance=thr, quantile=0.9, median_mid_btcusdt=m_btc,
             median_mid_ethusdt=m_eth, order_size_eth=round(size, 3), lot=0.001)
    ETH_FILE.parent.mkdir(parents=True, exist_ok=True)
    ETH_FILE.write_text(json.dumps(d, indent=1))
    return d


def main(argv):
    if len(argv) != 4 or argv[3] not in ("next", "status"):
        print(__doc__); return 2
    source, sym, day, what = argv
    try:
        if what == "status":
            role, us, done = state(source, sym, day)
            print(json.dumps(dict(role=role, units=us, done=done)))
        else:
            run_next(source, sym, day)
    except Refused as e:
        print("Refusing:", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
