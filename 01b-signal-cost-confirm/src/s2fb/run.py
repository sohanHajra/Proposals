"""The 01.b runner. One listed day, one unit at a time, each unit once.

Usage
  python -m s2fb.run SOURCE SYM DAY next     run the next unit of that day
  python -m s2fb.run SOURCE SYM DAY status   list the units and which are done
  python -m s2fb.run SOURCE SYM DAY leave_out "REASON"   a day whose file failed (copy, MD5 or read)
  python -m s2fb.run SOURCE SYM DAY explore NAME   an exploratory follow up from s2fb.explore, once,
                                                   only after the day's c2 has run (results/exploratory/NAME/)

SOURCE is cryptostruct, tardis or bybit. Only the days in s2fb.days are accepted, plus 2026-09-01
for building. Every unit writes its own file under results/ROLE/SOURCE_SYM_DAY/ and refuses to start
if that file is already there, so nothing is rerun. Units run in a fixed order, each in its own
process, because the machine I run on stops any job after 20 minutes.

  convert_tt   CryptoStruct top of book and trades to parquet
  convert_depth  CryptoStruct five levels from the depth stream
  convert      Bybit book and trades to parquet (Tardis needs none)
  audit        checks and the gap rule decision. A day the rule leaves out stops here
  threshold    on 2026-09-01 only. The ETHUSDT threshold and size, or Bybit's threshold, stored once
  c1           C1 with the drift and arrival split, race sensitivity and secondary checks
  c1_frozen    Bybit only. C1 again under the frozen 01 threshold, reported next to the main row
  c1_own       Bybit 2026-09-01 only. C1 under Bybit's own threshold (its c1 ran under the frozen one)
  c2_after     fixed price replay, random decisions, primary tie rule (arrays kept in data/derived)
  c2_before    the same with the other tie rule
  c2           C2 and its secondary checks from the two replays

ETHUSDT days are refused until every BTCUSDT test day has finished or been left out by the gap rule.
Any day other than 2026-09-01 is refused if the 01 code differs from tag v0.1-signal-to-fill.
"""
import hashlib
import json
import os
import re
import resource
import subprocess
import sys
import time

import numpy as np

from .paths import RESULTS, DERIVED, REPO, S2F_TAG
from .days import BUILD_DAY, TEST_DAYS
from .guard import check_day_allowed, Refused, runner

QTY_BTC = 0.01
TICK = {"BTCUSDT": 0.1, "ETHUSDT": 0.01}
ETH_FILE = RESULTS / "eth" / "threshold_ETHUSDT_2026-09-01.json"
BYBIT_FILE = RESULTS / "bybit" / "threshold_bybit_BTCUSDT_2026-09-01.json"


def units(source, sym, day):
    u = []
    if source == "cryptostruct":
        u += ["convert_tt", "convert_depth"]
    elif source == "bybit":
        u.append("convert")
    u.append("audit")
    if sym == "ETHUSDT" and day == BUILD_DAY:
        u.append("threshold")
    if source == "bybit" and day == BUILD_DAY:
        # built before the Deviation that gave Bybit its own threshold, so the two new units come last
        return u + ["c1", "c2_after", "c2_before", "c2", "threshold", "c1_own"]
    u.append("c1")
    if source == "bybit":
        u.append("c1_frozen")
    u += ["c2_after", "c2_before", "c2"]
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


def threshold_and_size(sym, source="tardis", unit="c1", day=None):
    """(threshold, order size). Binance BTCUSDT uses the frozen 01 value. Bybit uses its own value
    from 2026-09-01 (Deviation, later still, 2026-11-23), except c1_frozen and the build day c1."""
    from s2f.signals import frozen_threshold
    if sym == "BTCUSDT":
        if source != "bybit" or unit == "c1_frozen" or (day == BUILD_DAY and unit == "c1"):
            return frozen_threshold(), QTY_BTC
        if not BYBIT_FILE.exists():
            raise Refused("Bybit's threshold has not been stored yet (bybit BTCUSDT 2026-09-01, unit threshold)")
        return json.loads(BYBIT_FILE.read_text())["threshold_abs_imbalance"], QTY_BTC
    if not ETH_FILE.exists():
        raise Refused("the ETHUSDT threshold has not been stored yet (tardis ETHUSDT 2026-09-01, unit threshold)")
    d = json.loads(ETH_FILE.read_text())
    return d["threshold_abs_imbalance"], d["order_size_eth"]


MANIFEST = REPO / "01b-signal-cost-confirm" / "data" / "MANIFEST.md"


def manifest_md5(name):
    """The MD5 written for a bought test file in data/MANIFEST.md before it was copied in."""
    for line in MANIFEST.read_text().splitlines():
        m = re.match(r"\|\s*(\S+)\s*\|\s*([0-9a-f]{32})\s*\|", line)
        if m and m.group(1) == name:
            return m.group(2)
    return None


def md5_ok(source, sym, day):
    """CryptoStruct test files must match their MANIFEST MD5. Raises Refused otherwise."""
    if source != "cryptostruct" or day == BUILD_DAY:
        return True
    from .cryptostruct import raw_file
    f = raw_file(day, sym)
    want = manifest_md5(f.name)
    if want is None:
        return True        # free samples, checked against the seller's MD5 when they landed
    if not f.exists():
        raise Refused(f"{f.name} is not copied in. If it can't be, use leave_out")
    h = hashlib.md5()
    with open(f, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    if h.hexdigest() != want:
        raise Refused(f"{f.name} MD5 {h.hexdigest()} differs from MANIFEST {want}. Use leave_out")
    return True


def leave_out(source, sym, day, reason):
    """Write the day's audit as left out because its file failed (Deviation of 2026-11-23, afternoon, item 2)."""
    role, us, done = state(source, sym, day)
    a = unit_file(source, sym, day, role, "audit")
    if a.exists():
        raise Refused(f"{a} exists already")
    if done:
        raise Refused(f"units already ran for {day}: {done}")
    res = dict(unit="audit", source=source, symbol=sym, day=day, role=role,
               gap_rule=dict(left_out=True, reason=f"file failed: {reason}"))
    a.parent.mkdir(parents=True, exist_ok=True)
    a.write_text(json.dumps(res, indent=1))
    print("wrote", a, flush=True)
    return res


def state(source, sym, day):
    role = check_day_allowed(day, sym, source)
    us = units(source, sym, day)
    done = [u for u in us if unit_file(source, sym, day, role, u).exists()]
    return role, us, done


def run_next(source, sym, day):
    role, us, done = state(source, sym, day)
    if day != BUILD_DAY and not s2f_unchanged():
        raise Refused(f"the 01 code differs from {S2F_TAG}")
    if day != BUILD_DAY and (os.environ.get("S2FB_DATA") or os.environ.get("S2FB_RESULTS")):
        raise Refused("S2FB_DATA or S2FB_RESULTS is set. Test days run only on the project folders")
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
    if not done:
        md5_ok(source, sym, day)
    t0 = time.time()
    with runner():
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
        return store_bybit_threshold() if source == "bybit" else store_eth_threshold()
    thr, qty = threshold_and_size(sym, source, unit, day)
    if unit == "c2":
        ra = dict(np.load(array_file(source, sym, day, "c2_after")))
        rb = dict(np.load(array_file(source, sym, day, "c2_before")))
        return dict(order_size=qty, C2=analysis.c2(ra, rb))
    prepped = load.prep(source, day, sym)
    book = prepped[0]
    if unit in ("c1", "c1_frozen", "c1_own"):
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


def store_bybit_threshold():
    """Bybit's threshold, the 90th percentile of |I| on the last top of book row per stamp on
    2026-09-01, with 01's own function, stored once."""
    from . import load
    from s2f.signals import threshold
    if BYBIT_FILE.exists():
        raise Refused(f"{BYBIT_FILE} exists. Bybit's threshold is computed once")
    thr = threshold(load.prep("bybit", BUILD_DAY, "BTCUSDT")[0])
    d = dict(day=BUILD_DAY, venue="bybit", symbol="BTCUSDT", threshold_abs_imbalance=thr, quantile=0.9)
    BYBIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    BYBIT_FILE.write_text(json.dumps(d, indent=1))
    return d


EXPLORE = ("c2_lose_race", "c2_lose_race_split")


def run_explore(source, sym, day, name):
    """Exploratory, after release. Reads the stored c2_after arrays and the day's book. Writes once."""
    from . import load, explore
    if name not in EXPLORE:
        raise Refused(f"{name} is not an exploratory step")
    role, us, done = state(source, sym, day)
    if "c2" not in done:
        raise Refused(f"c2 has not run for {source} {sym} {day}")
    if day != BUILD_DAY and not s2f_unchanged():
        raise Refused(f"the 01 code differs from {S2F_TAG}")
    if day != BUILD_DAY and (os.environ.get("S2FB_DATA") or os.environ.get("S2FB_RESULTS")):
        raise Refused("S2FB_DATA or S2FB_RESULTS is set. Test days run only on the project folders")
    out = RESULTS / "exploratory" / name / f"{source}_{sym}_{day}.json"
    if out.exists():
        raise Refused(f"{out} exists, not overwriting it")
    t0 = time.time()
    with runner():
        r = dict(np.load(array_file(source, sym, day, "c2_after")))
        book = load.prep(source, day, sym)[0]
        res = getattr(explore, name)(r, book)
    res = {**res, **dict(step=name, source=source, symbol=sym, day=day, role=role, seconds=round(time.time() - t0, 1))}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=float))
    print("wrote", out, flush=True)
    return res


def main(argv):
    if not ((len(argv) == 4 and argv[3] in ("next", "status")) or (len(argv) == 5 and argv[3] in ("leave_out", "explore"))):
        print(__doc__); return 2
    source, sym, day, what = argv[:4]
    try:
        if what == "leave_out":
            leave_out(source, sym, day, argv[4])
        elif what == "explore":
            run_explore(source, sym, day, argv[4])
        elif what == "status":
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
