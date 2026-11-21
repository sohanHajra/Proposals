"""Run every registered analysis once on one test day or breadth day.

Usage  python -m s2f.run_test_day DATE

The date is the only input. It must be one of the two registered test days or the six registered
breadth days. Everything else is fixed here and in the modules as committed. The seed is 20261115,
the signal threshold is the stored dev day value, and the steps run in the order below. It refuses
to start if any output for that date already exists, so each day runs once. If a run stops part way,
its files stay where they are and a second start refuses. What to do then is a decision to write
down, not something this script does.

Test days, in order
  audit, sanity, tie_share, taker (H1), passive (H2), fixed_price (H5), taker_followups,
  passive_followups, robustness (checks 1, 3, 5, 6 and 8), placebo_h2 (check 7 for H2), jumps
Breadth days (secondary, registered 2026-11-19), in order
  audit, sanity, tie_share, taker, passive, fixed_price, taker_followups, passive_followups
Robustness and the jump split were registered for the test days only, so breadth days skip them.

Outputs are named by the date, e.g. results/taker/taker_2026-10-01.json.

Parts  python -m s2f.run_test_day DATE --part K
The remote worker I run on stops any single job after 20 minutes, and a whole test day takes about half
an hour, so the first start on 2026-10-01 stopped inside the robustness step. A part runs a fixed
slice of the same steps, in the same order, with the same code and seed, in its own process. Parts
are fixed below and must run in order. Part K refuses unless every output of the parts before it
exists and no output of part K or later exists. The passive follow ups are split by replay, and
each replay already writes its own saved arrays, so nothing about a replay changes.
"""
import gc
import json
import os
import sys
from pathlib import Path

from .paths import RAW, RESULTS, DATA, DEV_DAY, result_path
from .get_data import TEST_DAYS, BREADTH_DAYS, DTYPES

REGISTERED_SEED = 20261115
STEPS_TEST = ("audit", "sanity", "tie_share", "taker", "passive", "fixed_price",
              "taker_followups", "passive_followups", "robustness", "placebo_h2", "jumps")
STEPS_BREADTH = STEPS_TEST[:8]


class Refused(Exception):
    pass


def steps_for(day):
    if day in TEST_DAYS:
        return STEPS_TEST
    if day in BREADTH_DAYS:
        return STEPS_BREADTH
    raise Refused(f"{day} is not a registered test day {TEST_DAYS} or breadth day {BREADTH_DAYS}")


def outputs(day, steps, root):
    """Every results file and saved array this run would write, as paths."""
    from . import robustness, passive_followups
    root = Path(root)
    rp = lambda sub, stem: result_path(sub, stem, day, root)
    files = {
        "audit": [root / "audit" / f"tardis_{day}.json"],
        "sanity": [root / "replay" / f"sanity_{day}.json"],
        "tie_share": [rp("taker", "tie_share")],
        "taker": [rp("taker", "taker")],
        "passive": [rp("passive", "passive")],
        "fixed_price": [rp("passive", "fixed_price")],
        "taker_followups": [rp("taker", "followups")],
        "passive_followups": [rp("passive", "followups")],
        "robustness": [rp("robustness", c) for c in robustness.CHECKS],
        "placebo_h2": [rp("robustness", "placebo_h2")],
        "jumps": [root / "jump" / f"jump_split_{day}.json"],
    }
    out = [p for s in steps for p in files[s]]
    return out


def derived_files(day, derived):
    from .passive_followups import CONFIGS
    return [Path(derived) / f"{c}_{day}.npz" for c in CONFIGS]


def check_inputs(day):
    missing = [f"binance-futures_{dt}_{day}_BTCUSDT.csv.gz" for dt in DTYPES
               if not (RAW / "tardis" / f"binance-futures_{dt}_{day}_BTCUSDT.csv.gz").exists()]
    if missing:
        raise Refused(f"raw files missing for {day}: {missing}. Download them first with get_data.")


def _write(p, res):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        raise Refused(f"{p} appeared during the run, not overwriting it")
    p.write_text(json.dumps(res, indent=1, default=float))
    print("wrote", p, flush=True)


def run_day(day, root=RESULTS, derived=None, allow_dev=False):
    """The run itself. root and derived move the outputs only for the dev day dry run.
    allow_dev is only for that dry run and never reachable from the command line."""
    if day == DEV_DAY and allow_dev:
        steps = STEPS_TEST
    else:
        steps = steps_for(day)
    from . import taker, passive, fixed_price, taker_followups, passive_followups, robustness, jumps
    from . import data_audit, sanity, tie_share, signals
    if taker.SEED != REGISTERED_SEED:
        raise Refused(f"seed is {taker.SEED}, registered seed is {REGISTERED_SEED}")
    thr = signals.frozen_threshold()                       # fails loudly if the stored value is gone
    derived = Path(derived) if derived is not None else DATA / "derived"
    planned = outputs(day, steps, root) + derived_files(day, derived)
    there = [str(p) for p in planned if p.exists()]
    if there:
        raise Refused("outputs for this date already exist, this day has been run. Not overwriting\n  " + "\n  ".join(there))
    check_inputs(day)
    os.environ["S2F_ALLOW_TEST_DAY"] = "1"
    passive_followups.DERIVED = derived
    root = Path(root)
    rp = lambda sub, stem: result_path(sub, stem, day, root)
    print(f"{day}  steps {steps}  seed {taker.SEED}  signal threshold {thr}", flush=True)
    prepped = None
    for s in steps:
        print("step", s, flush=True)
        if s == "audit":
            _write(root / "audit" / f"tardis_{day}.json", data_audit.audit(day))
        elif s == "sanity":
            _write(root / "replay" / f"sanity_{day}.json", sanity.results(day))
        elif s == "tie_share":
            _write(rp("taker", "tie_share"), tie_share.results(day))
        elif s == "taker":
            _write(rp("taker", "taker"), taker.results(day))
        else:
            if prepped is None:
                prepped = passive.prep_day(day)
            if s == "passive":
                _write(rp("passive", "passive"), passive.results(day, prepped))
            elif s == "fixed_price":
                _write(rp("passive", "fixed_price"), fixed_price.results(day, prepped))
            elif s == "taker_followups":
                _write(rp("taker", "followups"), taker_followups.results(day, prepped))
            elif s == "passive_followups":
                passive_followups.run_configs(day, passive_followups.CONFIGS, prepped)
                if rp("passive", "followups").exists():
                    raise Refused("passive follow ups file appeared during the run")
                res = passive_followups.summarize(day, root)
                if not all(res["rerun_check"].values()):
                    print("WARNING rerun check failed", res["rerun_check"], flush=True)
            elif s == "robustness":
                same_clock = tuple(c for c in robustness.CHECKS if c != "local_order")
                robustness.run_checks(day, same_clock, root=root, derived=derived, prepped=prepped)
                prepped = None                     # free the exchange time arrays before the local clock load
                gc.collect()
                robustness.run_checks(day, ("local_order",), root=root, derived=derived)
            elif s == "placebo_h2":
                passive_followups.placebo(day, root=root, derived=derived, prepped=prepped)
            elif s == "jumps":
                _write(root / "jump" / f"jump_split_{day}.json", jumps.results(day))
    print("done", day, flush=True)


def _units(day):
    """Each step of the day as small units, in the registered order."""
    from .passive_followups import CONFIGS
    from . import robustness
    u = []
    for s in steps_for(day):
        if s == "passive_followups":
            u += [("pf_config", c) for c in CONFIGS] + [("pf_summary", None)]
        elif s == "robustness":
            u += [("rob", c) for c in robustness.CHECKS]
        else:
            u.append((s, None))
    return u


# fixed grouping of units into parts, by position in _units, written before any part was run
PART_BREAKS_TEST = (7, 11, 15, 20, 22, 23, 24, 25, 27)    # parts end after these unit counts
PART_BREAKS_BREADTH = (7, 11, 15, 20)


def parts(day):
    u = _units(day)
    br = PART_BREAKS_TEST if day in TEST_DAYS else PART_BREAKS_BREADTH
    assert br[-1] == len(u), (br, len(u))
    out, a = [], 0
    for b in br:
        out.append(u[a:b]); a = b
    return out


def unit_outputs(day, unit, root, derived):
    kind, arg = unit
    root, derived = Path(root), Path(derived)
    rp = lambda sub, stem: result_path(sub, stem, day, root)
    if kind == "pf_config":
        return [derived / f"{arg}_{day}.npz"]
    if kind == "pf_summary":
        return [rp("passive", "followups")]
    if kind == "rob":
        return [rp("robustness", arg)]
    return outputs(day, (kind,), root)


def run_part(day, k, root=RESULTS, derived=None):
    """Part k (1 based) of the day. Same calls as run_day, one slice at a time."""
    steps_for(day)
    P = parts(day)
    if not 1 <= k <= len(P):
        raise Refused(f"{day} has parts 1 to {len(P)}")
    from . import taker, passive, fixed_price, taker_followups, passive_followups, robustness, jumps
    from . import data_audit, sanity, tie_share, signals
    if taker.SEED != REGISTERED_SEED:
        raise Refused(f"seed is {taker.SEED}, registered seed is {REGISTERED_SEED}")
    thr = signals.frozen_threshold()
    derived = Path(derived) if derived is not None else DATA / "derived"
    before = [p for part in P[:k - 1] for u in part for p in unit_outputs(day, u, root, derived)]
    after = [p for part in P[k - 1:] for u in part for p in unit_outputs(day, u, root, derived)]
    missing = [str(p) for p in before if not p.exists()]
    if missing:
        raise Refused("earlier parts are not complete, missing\n  " + "\n  ".join(missing))
    there = [str(p) for p in after if p.exists()]
    if there:
        raise Refused("outputs for this part or a later one already exist. Not overwriting\n  " + "\n  ".join(there))
    check_inputs(day)
    os.environ["S2F_ALLOW_TEST_DAY"] = "1"
    passive_followups.DERIVED = derived
    root = Path(root)
    rp = lambda sub, stem: result_path(sub, stem, day, root)
    print(f"{day}  part {k} of {len(P)}  units {P[k - 1]}  seed {taker.SEED}  signal threshold {thr}", flush=True)
    prepped = None
    need_prep = {"passive", "fixed_price", "taker_followups", "pf_config"}
    for kind, arg in P[k - 1]:
        print("unit", kind, arg or "", flush=True)
        if kind in need_prep and prepped is None:
            prepped = passive.prep_day(day)
        if kind == "audit":
            _write(root / "audit" / f"tardis_{day}.json", data_audit.audit(day))
        elif kind == "sanity":
            _write(root / "replay" / f"sanity_{day}.json", sanity.results(day))
        elif kind == "tie_share":
            _write(rp("taker", "tie_share"), tie_share.results(day))
        elif kind == "taker":
            _write(rp("taker", "taker"), taker.results(day))
        elif kind == "passive":
            _write(rp("passive", "passive"), passive.results(day, prepped))
        elif kind == "fixed_price":
            _write(rp("passive", "fixed_price"), fixed_price.results(day, prepped))
        elif kind == "taker_followups":
            _write(rp("taker", "followups"), taker_followups.results(day, prepped))
        elif kind == "pf_config":
            passive_followups.run_configs(day, [arg], prepped)
        elif kind == "pf_summary":
            res = passive_followups.summarize(day, root)
            if not all(res["rerun_check"].values()):
                print("WARNING rerun check failed", res["rerun_check"], flush=True)
        elif kind == "rob":
            robustness.run_checks(day, (arg,), root=root, derived=derived)
        elif kind == "placebo_h2":
            passive_followups.placebo(day, root=root, derived=derived)
        elif kind == "jumps":
            _write(root / "jump" / f"jump_split_{day}.json", jumps.results(day))
    print("done", day, "part", k, flush=True)


def main(argv):
    if len(argv) == 3 and argv[1] == "--part" and argv[2].isdigit():
        try:
            run_part(argv[0], int(argv[2]))
        except Refused as e:
            print("Refusing:", e, file=sys.stderr)
            return 1
        return 0
    if len(argv) != 1:
        print(__doc__)
        return 2
    try:
        run_day(argv[0])
    except Refused as e:
        print("Refusing:", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
