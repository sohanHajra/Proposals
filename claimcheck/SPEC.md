# Claim format

## The tag in markdown

A claim tag is an HTML comment placed directly after the number it covers, with no space between them.

```markdown
Waiting 500 ms moved the taker's shortfall by 0.0040 bps<!--c:taker.dS500--> on the dev day.
```

GitHub renders this as plain text with the comment hidden. The checker reads the number before the tag (sign, digits, thousands commas, decimal point, and an optional `%`) and the claim id inside it. One short unit word may sit between the number and the tag, as `bps` does above. Anything else in between and the tag fails with no number found.

The word `negative` right before the number counts as its sign, since the notes write negative 0.0034 and not a minus sign. A number with both the word and a sign fails.

Tags inside fenced code blocks or inline code are not read, so the format can be shown in docs without becoming a claim. A comment that starts like a tag but is not exactly `<!--c:id-->` fails as malformed.

Claim ids use letters, digits, dots and underscores, and must be unique within a proposal. A good id says where the number comes from, for example `taker.dS500` or `passive.front.fill500`.

One number gets one tag. If the same number appears in two places, both carry the same tag.

## The entry in claims.yaml

Each proposal folder holds one `claims.yaml`. Every key is a claim id.

```yaml
taker.dS500:
  file: results/taker/taker_dev_2026-09-01.json
  path: primary_tie_after.by_delay.500.mean_dS_bps
  value: 0.0040
  tol: 0.00005
  unit: bps
```

| Field | Meaning |
|---|---|
| `file` | Results file, relative to the proposal folder. JSON for now. |
| `path` | Dotted path to the field. Each part is a dict key, or a list index written as a number. A key that contains dots goes in square brackets, so `quantiles.[0.5]` reads the key `0.5`. |
| `value` | The number as I state it in prose. |
| `tol` | How far the field in the file may sit from `value` and still pass. |
| `unit` | Optional. Shown in the report, not compared. |
| `scale` | Optional. Multiplies the field before comparing, for a share stored as 0.031 and written as 3.1%. Default 1. |

## When a claim passes

All three must hold.

1. The file exists and the path resolves to a number.
2. `abs(field * scale - value) <= tol`. A field exactly on the edge passes, so a stored 0.6455 written as 0.646 with tol 0.0005 is fine even though binary floats land a hair past it.
3. The number printed before each tag equals `value` once `value` is rounded to the number of decimals printed. A printed `%` is part of the text and is not converted.

## Example of a failure

If the results file is rerun and the field becomes 0.0061, the claim above fails on rule 2 and the report names the claim, the file, the field, the stored value and the new one. If the prose says 0.0041 while `value` is 0.0040, it fails on rule 3. Either way the command exits with code 1.

## Numbers with no tag

The check reads README.md, LAB_NOTEBOOK.md and FINAL_REPORT.md at the top of the proposal folder and lists every number that has no tag after it. It skips the same code blocks and inline code as the tag scan, plus blockquotes, text in double quotes, link targets, URLs, DOIs, arXiv ids, ISO dates, dates with a month name, clock times, four digit years, integers with a leading zero, ordered list markers, and numbers glued to letters, underscores, slashes or hyphens. Numbers right after Table, Figure, Section, page, Step, Appendix, Proposition, Lemma, seed and a few similar words are skipped too.

Two marks clear a number by hand. Neither is a claim and neither is checked against a file.

```markdown
Their taker fee was 1.7 bps<!--cite--> (Table 1).
The order waits 500 ms<!--nc--> before it is sent.
```

A proposal can also keep `claimcheck_ignore.txt` next to its `claims.yaml`. Each line is a phrase, matched exactly and only as a whole (the phrase `1 ms` does not match inside `0.1 ms` or `21 ms`), and numbers inside it are not listed.

```text
# design settings, not results
500 ms
10 level
```

These are warnings. They never change the exit code.

## Sources

The check reads the proposal's `LITERATURE_REVIEW.md`. With no such file the source checks are skipped and the report says so.

Reading depth. Any table whose header has a column named `Read at`, `Reading depth` or `Depth` is a list of sources. Each row's depth cell must contain `full text`, `abstract` or `listing`. Words around it are fine, and the first of the three in the cell is the depth reported. An empty cell, or one like `skimmed`, fails. A review with no such table fails.

```markdown
| Work | What it shows | Read at |
|---|---|---|
| Lee & Park (2020), *Queues* | Queue position matters | full text, appendix not read |
```

Unverified. A heading with the word Unverified in it starts the list of works I have not opened. It runs until the next heading at the same level or higher. Each bullet must start with the authors and a year in brackets, as in `Smith & Jones (2019), *Title*`, so the check can take the first author's surname and the year. A bullet it can't read that way fails rather than being skipped. A review with no Unverified heading fails; an empty list under the heading is fine.

```markdown
## Unverified
- Smith & Jones (2019), *Implementation shortfall*, Journal C.
```

Every markdown file in the proposal is then searched for each unverified work, apart from the Unverified list itself, INTEGRITY_LOG.md, code, and anything under `data/` or a dot folder. A hit is the surname as a whole word with the year after it on the same line, at most 60 characters on. `Smith (2019)`, `Smith 2019`, `Smith, 2019` and `Smith et al. (2019)` all count. A hit fails unless `<!--unread-->` comes right after it, which marks a mention for context.

```markdown
The benchmark goes back to Smith (2019)<!--unread-->, which I have not read yet.
```

A work that has a row in a depth table and also sits on the Unverified list fails, since it can't be both.

What this can't catch. A mention by surname alone, a work cited under a second author's name, or a depth that is written down but not true.

## Preregistration order

The check reads the proposal's `PREREGISTRATION.md` and the git history of the repo it sits in. With no such file the check is skipped and the report says so. A preregistration that exists but has never been committed fails.

Test day results. Files under `results/` in the proposal folder whose path holds one of the test dates. The dates are every ISO date on a table row whose first cell is `Test` or `Test days`.

```markdown
| Role | Data | Days |
|---|---|---|
| Dev | Same files | 2026-09-01 |
| Test | Same files | 2026-10-01 and 2026-11-01 |
```

Files the table can't name go in `claimcheck_tests.txt` next to the preregistration, one glob per line, relative to the proposal folder. Lines starting with `#` are comments. Files git ignores are never counted.

```text
# breadth days, run after the registered tests
results/breadth/*.json
```

Order. The commit that first added PREREGISTRATION.md must be a strict ancestor of the commit that first added each test day results file. The same commit fails. A results file that is in the folder but not committed passes as long as the preregistration is committed.

Edits after the lock. The lock is the first commit that brings in a test day result, or the working tree when the only results are uncommitted. Every line added, changed or removed in PREREGISTRATION.md from the lock on, in commits and in the working tree, must sit under a heading containing the word Deviations, at any depth below it. For a removed line that means where it sat before the change. Renaming a heading to start a Deviations section fails on the old heading line. When the order check already fails, edits are not listed, since the whole file came after the results.

What this can't catch. It reads commit order, so a rewritten history can fool it. A results file is dated by the first commit at its current path, so a rename resets the date. A test day that was looked at but whose results never reached the folder leaves no trace here.
