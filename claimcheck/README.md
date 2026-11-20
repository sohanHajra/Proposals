# claimcheck

A small checker that ties every number I write about a result back to the file that produced it. If the prose and the data disagree, the check fails.

It lives at the top of the repo, outside any one proposal, so each proposal can use it with its own `claims.yaml`.

## What it checks

1. **Numbers match results.** Every number in public prose that reports a result carries a claim tag. The tag names an entry in the proposal's `claims.yaml`, and that entry names a results file, a field inside it, the value I wrote down, and a tolerance. The check rereads the file and fails if the field has moved outside the tolerance, if the field or file is missing, if a tag has no entry, or if the number printed in the prose is not the entry's value at the printed precision.
2. **Untagged numbers.** Numbers in README, LAB_NOTEBOOK and FINAL_REPORT that carry no tag are listed as warnings. Dates, clock times, years, ids, DOIs, arXiv ids, links, file names, quotes and code are skipped, and so are numbers right after words like Table, Section or page. It can't tell a result from a setting I chose, so 500 ms of injected delay gets listed just like a measured shortfall. That is why these are warnings and not failures.
3. **Sources.** Every row of the literature review table states how deeply I read the work (full text, abstract, or listing only). Nothing on the Unverified list is cited anywhere else in the proposal. A citation here means the first author's surname with the year after it on the same line, so `Perold (1988)` counts and a bare `Perold` does not. If I mention an unread work for context, `<!--unread-->` right after the citation says I don't lean on it. INTEGRITY_LOG.md is not searched, since saying what I have and haven't read is its job. A work listed both as read and as unverified fails too.
4. **Preregistration order.** Using git history, PREREGISTRATION.md was first committed before the first commit of any test day results file. Later edits to it are flagged unless they sit under a Deviations heading.

The claim format is written out in [SPEC.md](SPEC.md).

## What it cannot check

It checks that a number matches a file. It does not check that the code which wrote the file is right, that the test is the right test, or that my reading of a result is fair. Logic, framing and bias still need a person reading cold, and what that reading finds goes in each proposal's INTEGRITY_LOG.md. A green run means the prose and the results agree. It does not mean the results are true.

## Status

The checks above are being built one at a time, and this table says which ones run. The first three do so far. The preregistration check is not run yet, so a green result today says nothing about it.

| Check | Runs |
|---|---|
| Numbers match results | yes |
| Untagged numbers | yes, as warnings |
| Sources | yes |
| Preregistration order | not yet |

## How to run

From the repo root, with Python 3.10 or newer and PyYAML.

```bash
python -m claimcheck 01-signal-to-fill
```

Exit codes. `0` means every check that ran passed. `1` means at least one failed. `2` means the run could not check anything (no `claims.yaml` or an empty one with no tags, and no LITERATURE_REVIEW.md). The report says which checks ran, so a proposal with a literature review but no `claims.yaml` yet can exit `0` with its numbers not checked.

The report lists every claim against its results file, then every tag in the proposal's markdown with its file and line. Claims that no tag uses are listed as warnings and do not fail the run.

After that come the source checks, one line per work in the review and one per citation of an unverified work. Add `--no-sources` to skip them.

Then comes the list of numbers with no tag, each with its file, line and a bit of the sentence around it. Add `--no-untagged` to leave that list out. To clear a warning, do one of three things.

- Tag the number if it reports a result.
- Put `<!--cite-->` right after a number quoted from a paper, or `<!--nc-->` right after one that is not a result (a delay I chose, a count of book levels).
- Add a phrase to `claimcheck_ignore.txt` in the proposal folder, one per line, for a setting that comes up again and again, like `500 ms`. Any number inside that phrase is skipped everywhere. Lines starting with `#` are comments.

The checker has its own tests, also run from the repo root.

```bash
python -m unittest discover claimcheck/tests
```

Each folder in `claimcheck/tests/fixtures/` is a tiny proposal built to pass or to fail one way (a wrong number in the prose, a results file that changed after a rerun, a missing field, a missing file, a tag with no entry, a broken tag). The `untagged` one mixes four plain untagged results in with every kind of number that should be skipped. The three `sources_` ones hold small literature reviews, one clean, one with missing depths and unread works cited as evidence, and one with no depth column and no Unverified list. The tests check that each one gives the right exit code and names the right problem.

## How a new proposal adopts it

1. Write results to JSON files inside the proposal folder, for example under `results/`.
2. Keep a LITERATURE_REVIEW.md with a `Read at` column and an Unverified section, even an empty one.
3. Add a `claims.yaml` in the proposal folder with one entry per number you report.
4. Put the tag right after each number in the markdown, for example `0.0040 bps<!--c:taker.dS500-->`. The tag is an HTML comment, so GitHub does not show it.
5. Run the command above before every push.
