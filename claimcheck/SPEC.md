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
