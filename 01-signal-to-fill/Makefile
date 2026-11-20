PY := .venv/bin/python
export PYTHONPATH := src

env:
	uv venv .venv --python 3.12 && uv pip install -r requirements.lock --python $(PY)

data:
	$(PY) -m s2f.get_data dev && $(PY) -m s2f.get_data lobster

audit:
	$(PY) -m s2f.data_audit 2026-09-01
	$(PY) -m s2f.lobster_audit

sanity:
	$(PY) -m s2f.sanity 2026-09-01
	$(PY) -m s2f.tie_share 2026-09-01

test:
	$(PY) -m pytest -q tests

.PHONY: env data audit test sanity taker passive fixed_price followups_taker followups_passive followups lobster jump robustness verify reproduce run_day dry_run

reproduce: env data audit test sanity taker passive fixed_price followups robustness lobster jump verify

taker:
	$(PY) -m s2f.taker 2026-09-01

passive:
	$(PY) -m s2f.passive 2026-09-01

fixed_price:
	$(PY) -m s2f.fixed_price 2026-09-01

# dev day follow ups (H1b and H2c intervals, RQ3 split, cost by arrival state, tie flip, signal decisions)
followups_taker:
	$(PY) -m s2f.taker_followups 2026-09-01

followups_passive:
	$(PY) -m s2f.passive_followups 2026-09-01 run
	$(PY) -m s2f.passive_followups 2026-09-01 summarize

followups: followups_taker followups_passive

# RQ2 order lifecycles and where cancellations land (LOBSTER, Nasdaq 2012-06-21)
lobster:
	$(PY) -m s2f.lobster_rq2

# jump moment split and stale top of book count (exploratory, added 2026-11-19)
jump:
	$(PY) -m s2f.jumps 2026-09-01

# every tagged number in the notes against its results file, plus the source and preregistration checks
# (claimcheck lives at the top of the repo, so it runs from there; exits 1 on any mismatch)
verify:
	cd .. && $(abspath $(PY)) -m claimcheck 01-signal-to-fill

# robustness checks 1, 3, 5, 6 and 8 on the dev day (after followups, which saves the passive arrays)
robustness:
	$(PY) -m s2f.robustness 2026-09-01

# one registered test or breadth day, run once, every output named by the date
# make run_day DAY=2026-10-01
run_day:
	$(PY) -m s2f.run_test_day $(DAY)

# the same steps on the dev day, written to a temporary folder and compared with the committed files
dry_run:
	$(PY) -m s2f.dry_run
