# claimcheck

A small checker that ties every number I write about a result back to the file that produced it. If the prose and the data disagree, the check fails.

It lives at the top of the repo, outside any one proposal, so each proposal can use it with its own `claims.yaml`.

## What it checks

1. **Numbers match results.** Every number in public prose that reports a result carries a claim tag. The tag names an entry in the proposal's `claims.yaml`, and that entry names a results file, a field inside it, the value I wrote down, and a tolerance. The check rereads the file and fails if the field has moved outside the tolerance, if the field or file is missing, if a tag has no entry, or if the number printed in the prose is not the entry's value at the printed precision.
2. **Untagged numbers.** Numbers in README, LAB_NOTEBOOK and FINAL_REPORT that look like results but carry no tag are listed as warnings. Dates, years, ids, DOIs, file names and code blocks are skipped.
3. **Sources.** Every entry in LITERATURE_REVIEW.md states how deeply I read it (full text, abstract, or listing only). Nothing on the Unverified list is cited elsewhere as evidence.
4. **Preregistration order.** Using git history, PREREGISTRATION.md was first committed before the first commit of any test day results file. Later edits to it are flagged unless they sit under a Deviations heading.

The claim format is written out in [SPEC.md](SPEC.md).

## What it cannot check

It checks that a number matches a file. It does not check that the code which wrote the file is right, that the test is the right test, or that my reading of a result is fair. Logic, framing and bias still need a person reading cold, and what that reading finds goes in each proposal's INTEGRITY_LOG.md. A green run means the prose and the results agree. It does not mean the results are true.

## Status

The package skeleton and the claim format are in place. The checks above are being built one at a time, and this section says which ones run. Right now none of them do, and the command exits with code 2 rather than pretending to pass.

| Check | Runs |
|---|---|
| Numbers match results | not yet |
| Untagged numbers | not yet |
| Sources | not yet |
| Preregistration order | not yet |

## How to run

From the repo root, with Python 3.10 or newer and PyYAML.

```bash
python -m claimcheck 01-signal-to-fill
```

Exit codes. `0` means every check passed. `1` means at least one claim failed. `2` means the run could not check anything (no `claims.yaml`, or a check that is not built yet).

## How a new proposal adopts it

1. Write results to JSON files inside the proposal folder, for example under `results/`.
2. Add a `claims.yaml` in the proposal folder with one entry per number you report.
3. Put the tag right after each number in the markdown, for example `0.0040 bps<!--c:taker.dS500-->`. The tag is an HTML comment, so GitHub does not show it.
4. Run the command above before every push.
