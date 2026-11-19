# Claim format

## The tag in markdown

A claim tag is an HTML comment placed directly after the number it covers, with no space between them.

```markdown
Waiting 500 ms moved the taker's shortfall by 0.0040 bps<!--c:taker.dS500--> on the dev day.
```

GitHub renders this as plain text with the comment hidden. The checker reads the number before the tag (sign, digits, thousands commas, decimal point, and an optional `%`) and the claim id inside it. One short unit word may sit between the number and the tag, as `bps` does above. Anything else in between and the tag fails with no number found.

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
| `path` | Dotted path to the field. Each part is a dict key, or a list index written as a number. Keys that contain dots are not supported yet. |
| `value` | The number as I state it in prose. |
| `tol` | How far the field in the file may sit from `value` and still pass. |
| `unit` | Optional. Shown in the report, not compared. |
| `scale` | Optional. Multiplies the field before comparing, for a share stored as 0.031 and written as 3.1%. Default 1. |

## When a claim passes

All three must hold.

1. The file exists and the path resolves to a number.
2. `abs(field * scale - value) <= tol`.
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

A proposal can also keep `claimcheck_ignore.txt` next to its `claims.yaml`. Each line is a phrase, matched exactly, and numbers inside it are not listed.

```text
# design settings, not results
500 ms
10 level
```

These are warnings. They never change the exit code.
