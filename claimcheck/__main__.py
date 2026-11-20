"""Command line entry point. Run from the repo root as `python -m claimcheck <proposal_dir>`."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .claims import ClaimsFileError, check_data, load_claims
from .scan import printed_matches, scan_dir
from .prereg import PREREG_FILE, GitError, check_prereg
from .sources import REVIEW_FILE, check_sources
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


def report_sources(root, out=print):
    """Reading depth and Unverified citations. Returns (checked, failures)."""
    rep = check_sources(root)
    out("")
    if not rep.found:
        out(f"Sources: no {REVIEW_FILE}, not checked")
        return False, 0
    out(f"Sources in {REVIEW_FILE}")
    for p in rep.problems:
        out(f"  FAIL  {p}")
    for r in rep.rows:
        if r.depth:
            out(f"  PASS  {REVIEW_FILE}:{r.line}  {r.work}  read at {r.depth}")
        else:
            out(f"  FAIL  {REVIEW_FILE}:{r.line}  {r.work}  no reading depth (full text, abstract or listing)")
    for e in rep.unverified:
        if e.problem:
            out(f"  FAIL  {REVIEW_FILE}:{e.line}  unverified entry  {e.problem}  ({e.text})")
    cited = {}
    for c in rep.citations:
        where = f"{c.file}:{c.line}"
        name = f"{c.entry.surname} {c.entry.year}"
        if c.marked:
            out(f"  PASS  {where}  {name} is unverified, marked as not relied on")
        else:
            out(f"  FAIL  {where}  {name} is on the Unverified list but cited here ({c.context})")
        cited.setdefault(id(c.entry), True)
    clean = [e for e in rep.unverified if not e.problem and id(e) not in cited]
    if clean:
        names = ", ".join(f"{e.surname} {e.year}" for e in clean)
        out(f"  PASS  unverified and not cited elsewhere: {names}")
    elif not rep.unverified and rep.unverified_section:
        out("  PASS  Unverified list is empty")
    return True, rep.failures


def report_prereg(root, out=print):
    """Preregistration committed before any test day results, and untouched after except Deviations."""
    out("")
    try:
        rep = check_prereg(root)
    except GitError as exc:
        out(f"Preregistration: {exc}")
        return True, 1
    if not rep.found:
        out(f"Preregistration: no {PREREG_FILE}, not checked")
        return False, 0
    out(f"Preregistration in {PREREG_FILE}")
    for p in rep.problems:
        out(f"  FAIL  {p}")
    if not rep.in_git or rep.prereg_commit is None:
        return True, rep.failures
    if rep.prereg_commit:
        out(f"  PASS  first committed in {rep.prereg_commit.short} on {rep.prereg_commit.date[:10]}")
    named = []
    if rep.test_dates:
        named.append("test dates " + ", ".join(rep.test_dates))
    if rep.patterns:
        named.append("patterns " + ", ".join(rep.patterns))
    if not named:
        out("  WARN  no test days named (no Test row in a table, no claimcheck_tests.txt), so no file counts as a test result")
    else:
        out(f"  test day results are files matching {'; '.join(named)}")
    if not rep.tests:
        if named:
            out("  PASS  no test day results in the folder yet")
        return True, rep.failures
    early = {t.path for t in rep.early}
    for t in rep.tests:
        if t.path in early:
            when = "in the same commit as" if t.commit.sha == rep.prereg_commit.sha else "before"
            out(f"  FAIL  {t.path} first committed in {t.commit.short} {when} the preregistration")
        elif t.commit is None:
            out(f"  PASS  {t.path} not committed yet, preregistration already is")
        else:
            out(f"  PASS  {t.path} first committed in {t.commit.short} on {t.commit.date[:10]}, after the preregistration")
    if rep.early:
        out("  edits after test results not checked, since the order already fails")
        return True, rep.failures
    lock = rep.lock
    lock_at = f"{lock.commit.short}" if lock.commit else "the working tree"
    for e in rep.edits:
        out(f"  FAIL  {e.where}  {PREREG_FILE}:{e.line} {e.kind} after test results arrived ({lock_at}), outside Deviations: {e.text.strip()[:70]}")
    if not rep.edits:
        extra = f", {rep.allowed_edits} changed line(s) under Deviations" if rep.allowed_edits else ""
        out(f"  PASS  no changes outside Deviations since test results arrived ({lock_at}){extra}")
    return True, rep.failures


def check_numbers(root, out=print):
    """Claims against results files and tags in markdown. Returns (checked, failures)."""
    claims_file = root / "claims.yaml"
    if not claims_file.is_file():
        out(f"Numbers: no claims.yaml in {root}, not checked")
        return False, 0
    try:
        claims = load_claims(claims_file)
    except ClaimsFileError as exc:
        out(f"claimcheck: {exc}")
        return True, 1

    tags = scan_dir(root)
    if not claims and not tags:
        out(f"Numbers: {claims_file} is empty and no tags found, not checked")
        return False, 0

    failures = 0
    cache = {}
    results = {cid: check_data(c, root, cache) for cid, c in claims.items()}

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
    return True, failures


def verify(root, out=print, untagged=True, sources=True, prereg=True):
    """Run every check on one proposal folder. Returns an exit code."""
    root = Path(root)
    out(f"claimcheck {__version__}: {root}")
    checked, failures = check_numbers(root, out)
    if sources:
        s_checked, s_failures = report_sources(root, out)
        checked = checked or s_checked
        failures += s_failures
    if prereg:
        p_checked, p_failures = report_prereg(root, out)
        checked = checked or p_checked
        failures += p_failures
    if untagged:
        report_untagged(root, out)

    out("")
    if failures:
        out(f"{failures} failure(s)")
        return EXIT_FAIL
    if not checked:
        out("nothing checked")
        return EXIT_NOTHING_CHECKED
    out("all checks agree")
    return EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="claimcheck",
        description="Check that numbers in a proposal's markdown match its results files.",
    )
    parser.add_argument("proposal_dir", help="proposal folder, for example 01-signal-to-fill")
    parser.add_argument("--no-untagged", action="store_true", help="skip the list of numbers with no tag")
    parser.add_argument("--no-sources", action="store_true", help="skip the reading depth and Unverified checks")
    parser.add_argument("--no-prereg", action="store_true", help="skip the preregistration order check")
    parser.add_argument("--version", action="version", version=f"claimcheck {__version__}")
    args = parser.parse_args(argv)

    root = Path(args.proposal_dir)
    if not root.is_dir():
        print(f"claimcheck: {root} is not a folder", file=sys.stderr)
        return EXIT_NOTHING_CHECKED
    return verify(root, untagged=not args.no_untagged, sources=not args.no_sources, prereg=not args.no_prereg)


if __name__ == "__main__":
    sys.exit(main())
