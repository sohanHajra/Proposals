"""Command line entry point. Run from the repo root as `python -m claimcheck <proposal_dir>`."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .claims import ClaimsFileError, check_data, load_claims
from .scan import printed_matches, scan_dir
from .untagged import scan_untagged

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_NOTHING_CHECKED = 2


def report_untagged(root, out=print):
    """List numbers in public prose with no tag. Warnings only. Returns how many were found."""
    found = scan_untagged(root)
    out("")
    if not found:
        out("Numbers with no tag: none")
        return 0
    out(f"Numbers with no tag (warning only, {len(found)})")
    for u in found:
        out(f"  WARN  {u.file}:{u.line}  {u.number}  {u.context}")
    return len(found)


def verify(root, out=print, untagged=True):
    """Run the numbers check on one proposal folder. Returns an exit code."""
    root = Path(root)
    claims_file = root / "claims.yaml"
    if not claims_file.is_file():
        out(f"claimcheck: no claims.yaml in {root}, nothing checked")
        if untagged:
            report_untagged(root, out)
        return EXIT_NOTHING_CHECKED
    try:
        claims = load_claims(claims_file)
    except ClaimsFileError as exc:
        out(f"claimcheck: {exc}")
        return EXIT_FAIL

    tags = scan_dir(root)
    if not claims and not tags:
        out(f"claimcheck: {claims_file} is empty and no tags found, nothing checked")
        if untagged:
            report_untagged(root, out)
        return EXIT_NOTHING_CHECKED

    failures = 0
    cache = {}
    results = {cid: check_data(c, root, cache) for cid, c in claims.items()}

    out(f"claimcheck {__version__}: {root}")
    out(f"{len(claims)} claims in claims.yaml, {len(tags)} tags in markdown")
    out("")
    out("Claims against results files")
    for cid in sorted(results):
        r = results[cid]
        c = r.claim
        if r.ok:
            unit = f" {c.unit}" if c.unit else ""
            out(f"  PASS  {cid}  {c.value:g}{unit}  ({c.file} {c.path} = {r.stored:.6g})")
        else:
            failures += 1
            out(f"  FAIL  {cid}  {r.reason}")

    out("")
    out("Tags in markdown")
    used = set()
    for t in tags:
        where = f"{t.file}:{t.line}"
        if t.problem:
            failures += 1
            out(f"  FAIL  {where}  {t.claim_id}  {t.problem}")
            continue
        used.add(t.claim_id)
        c = claims.get(t.claim_id)
        if c is None:
            failures += 1
            out(f"  FAIL  {where}  {t.claim_id}  tag has no entry in claims.yaml")
            continue
        if c.errors:
            failures += 1
            out(f"  FAIL  {where}  {t.claim_id}  its claims.yaml entry is broken")
            continue
        shown = t.printed + ("%" if t.pct else "")
        if not printed_matches(t.printed, c.value):
            failures += 1
            out(f"  FAIL  {where}  {t.claim_id}  prose says {shown}, claim value is {c.value:g}")
        else:
            out(f"  PASS  {where}  {t.claim_id}  {shown}")

    unused = sorted(set(claims) - used)
    if unused:
        out("")
        out("Claims never cited in markdown (warning only)")
        for cid in unused:
            out(f"  WARN  {cid}")

    if untagged:
        report_untagged(root, out)

    out("")
    if failures:
        out(f"{failures} failure(s)")
        return EXIT_FAIL
    out("all claims and tags agree")
    return EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="claimcheck",
        description="Check that numbers in a proposal's markdown match its results files.",
    )
    parser.add_argument("proposal_dir", help="proposal folder, for example 01-signal-to-fill")
    parser.add_argument("--no-untagged", action="store_true", help="skip the list of numbers with no tag")
    parser.add_argument("--version", action="version", version=f"claimcheck {__version__}")
    args = parser.parse_args(argv)

    root = Path(args.proposal_dir)
    if not root.is_dir():
        print(f"claimcheck: {root} is not a folder", file=sys.stderr)
        return EXIT_NOTHING_CHECKED
    return verify(root, untagged=not args.no_untagged)


if __name__ == "__main__":
    sys.exit(main())
