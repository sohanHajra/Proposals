# Using claimcheck in a new proposal

This is how I set up a new proposal folder so claimcheck can check it from day one, with real examples from [01 From Signal to Fill](../01-signal-to-fill/), the first proposal it was used on. The format itself is in [SPEC.md](SPEC.md). What each check does and what it can't do is in the [README](README.md).

The short version. Copy [`starter/`](starter/) into a new numbered folder, replace the example content, and keep `make verify` passing as the proposal grows. The starter passes as it stands, and its own test in `tests/test_starter.py` makes sure it keeps passing and fails when a number drifts.

```bash
cp -r claimcheck/starter 02-my-question
cd 02-my-question && make verify
```

## In the order the work happens

### 1. Before any code

Write the literature review with a `Read at` column, and an Unverified section for works I have only seen cited. The section can be empty, but the heading has to be there.

In 01 each row ends with how far I got, for example `full text` for Danait, Zamora & Boier (2026), and the Unverified list holds four works I never opened at the source. The check fails if a row has no depth, or if one of those four is cited anywhere else in the proposal as if I had read it.

### 2. The preregistration, committed before any test data

The data table needs a row whose first cell is `Test`, with the test dates written as ISO dates. That row is how the check knows which results files are test day results. In 01 it reads

```markdown
| Test | Same files | 2026-10-01 and 2026-11-01, each analysed on its own |
```

End the file with a `## Deviations` heading. After the first test day result is committed, any change to the preregistration outside that heading fails the check.

If some test results won't have a test date in their path, list globs for them in `claimcheck_tests.txt`. 01 added six breadth days this way, after registering them under Deviations and before downloading any of them.

```text
results/*2026-03-01*
results/*2026-04-01*
```

### 3. Results go to JSON, not just to the notebook

Every number I plan to write about should exist in a results file inside the proposal folder. In 01 the dev day taker run writes `results/taker/taker_dev_2026-09-01.json`, and inside it the mean extra shortfall at 500 ms sits at `primary_tie_after.by_delay.500.mean_dS_bps` with the value `0.003952141524279496`.

A number worked out by hand from two other numbers (a difference, a ratio) is the one most likely to be wrong, so it is better to have the code write it to the file too. 01 learned this the hard way, see the last section.

### 4. One claims.yaml entry per number

The entry says where the number lives, what I wrote, and how far apart the two may be. I set `tol` to half a unit of the last printed digit, so a value printed to four decimals gets `0.00005`.

```yaml
taker.dS500:
  file: results/taker/taker_dev_2026-09-01.json
  path: primary_tie_after.by_delay.500.mean_dS_bps
  value: 0.0040
  tol: 0.00005
```

A share stored as a fraction (0.1258 in the file) and written as 12.6% takes `scale: 100`.

```yaml
taker.h1b.share:
  file: results/taker/taker_dev_2026-09-01.json
  path: primary_tie_after.H1b_dS100.share_positive
  value: 12.6
  tol: 0.05
  scale: 100
```

A JSON key that itself contains a dot goes in brackets, as in `feed_latency_ms_bt_quantiles.[0.5]`.

Ids are worth keeping readable (`taker.dS500`, `passive.front.fill500`). Months later the id is what tells me which run a number came from.

### 5. Tag the number in the notes

The tag goes right after the number, with at most one short unit word in between. On GitHub it doesn't show.

```markdown
Mean extra shortfall at 500 ms over 1 ms is 0.0040<!--c:taker.dS500--> bps (95% block bootstrap interval negative 0.0034<!--c:taker.dS500.lo--> to 0.0114<!--c:taker.dS500.hi-->).
```

The same number in two places gets the same tag in both.

### 6. Clear the numbers that aren't results

The untagged list will be long at first. It lists every number it can't rule out, including ones I chose. There are three ways to clear one.

* A number quoted from a paper gets `<!--cite-->`, as in 01's "1.7<!--cite--> bps (Table 1)" for the Binance taker fee Albers et al. report.
* A one off number that isn't a result gets `<!--nc-->`, like the HTTP 200 a download returned.
* A setting that keeps coming back goes in `claimcheck_ignore.txt` as a whole phrase. 01 lists its delay grid, its order size `0.01 BTC`, and its H1 bar `0.1 bps` there.

Untagged numbers never fail the run, but I want the list at zero before a proposal is released, so every result in the notes is either tagged or plainly not a result.

### 7. Run it

Add a `verify` target to the proposal's Makefile. The starter's version works for any folder name.

```make
verify:
	cd .. && python3 -m claimcheck $(notdir $(CURDIR))
```

01 runs it with its own pinned venv and also as the last step of `make reproduce`. The same check runs on every push through GitHub Actions, on every numbered folder.

## What a failure looked like in 01

When I first tagged the dev day passive results, one line failed. The 18 November notebook entry said the matched 10 s markout under the front rule was better at 500 ms by 0.067<!--nc--> bps. I had subtracted two rounded means by hand. The results file gives 0.0665, which rounds to 0.066. The conclusion didn't change, but the number was wrong.

I didn't edit the old entry to make it pass. It keeps its words with a pointer, the wrong figure is marked `<!--nc-->` so it isn't counted as a claim, and a new dated entry explains the slip. That is what I'd do in any proposal. When the check fails, fix the prose or log the correction, and never move `value` or `tol` just to make it agree.

## What adopting it does not give you

A green run means the notes report what the code wrote. It says nothing about whether the code is right, whether the test answers the question, or whether my reading of the result is fair. Those still need a careful reread, and that goes in the proposal's INTEGRITY_LOG.md.
