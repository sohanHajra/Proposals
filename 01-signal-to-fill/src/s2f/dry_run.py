"""Dev day dry run of the test day runner, written to a temporary folder.

Usage  python -m s2f.dry_run

Runs every test day step on 2026-09-01 with outputs in a new temporary folder, so nothing under
results/ or data/derived is touched and no test day file is read. Then compares each output that
has a committed dev day counterpart and writes the comparison to <tmp>/dry_run_check.json.
"""
import json
import sys
import tempfile
from pathlib import Path

from .paths import RESULTS, DEV_DAY
from .run_test_day import run_day

PAIRS = [("audit/tardis_{d}.json", "audit/tardis_{d}.json"),
         ("replay/sanity_{d}.json", "replay/sanity_{d}.json"),
         ("taker/tie_share_dev_{d}.json", "taker/tie_share_dev_{d}.json"),
         ("taker/taker_dev_{d}.json", "taker/taker_dev_{d}.json"),
         ("passive/passive_dev_{d}.json", "passive/passive_dev_{d}.json"),
         ("passive/fixed_price_dev_{d}.json", "passive/fixed_price_dev_{d}.json"),
         ("taker/followups_dev_{d}.json", "taker/followups_dev_{d}.json"),
         ("passive/followups_dev_{d}.json", "passive/followups_dev_{d}.json"),
         ("jump/jump_split_{d}.json", "jump/jump_split_{d}.json")]


def diff(a, b, path=""):
    """Paths where two json values differ (numbers beyond 1e-12 relative, or anything else)."""
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}.{k} only in {'dry run' if k in a else 'committed'}")
            else:
                out += diff(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if abs(a - b) > 1e-12 * max(1.0, abs(a), abs(b)):
            out.append(f"{path} {b} -> {a}")
    elif a != b:
        out.append(f"{path} {b!r} -> {a!r}")
    return out


def main():
    tmp = Path(tempfile.mkdtemp(prefix="s2f_dryrun_"))
    print("dry run folder", tmp, flush=True)
    run_day(DEV_DAY, root=tmp / "results", derived=tmp / "derived", allow_dev=True)
    check = {}
    for new, old in PAIRS:
        n = tmp / "results" / new.format(d=DEV_DAY); o = RESULTS / old.format(d=DEV_DAY)
        if not n.exists() or not o.exists():
            check[new] = dict(missing=[str(x) for x in (n, o) if not x.exists()]); continue
        d = diff(json.loads(n.read_text()), json.loads(o.read_text()))
        check[new] = dict(n_differences=len(d), differences=d[:200])
    robust = sorted(str(p.relative_to(tmp)) for p in (tmp / "results" / "robustness").glob("*.json"))
    rcheck = {}
    for p in robust:
        o = RESULTS / Path(p).relative_to("results")
        if o.exists():
            d = diff(json.loads((tmp / p).read_text()), json.loads(o.read_text()))
            rcheck[p] = dict(n_differences=len(d), differences=d[:50])
    res = dict(folder=str(tmp), compared_with_committed=check, robustness_files=robust,
               robustness_compared=rcheck)
    (tmp / "dry_run_check.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v.get("n_differences", v) for k, v in {**check, **rcheck}.items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
