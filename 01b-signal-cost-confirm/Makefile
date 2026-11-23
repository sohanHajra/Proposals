# Run from the proposal folder. The 01 environment and code are reused as they are at tag v0.1-signal-to-fill.
PY := ../01-signal-to-fill/.venv/bin/python
export PYTHONPATH := src

env:
	$(MAKE) -C ../01-signal-to-fill env

test:
	$(PY) -m pytest -q -m "not slow" tests

test_slow:
	$(PY) -m pytest -q -m slow tests

# CryptoStruct 2026-09-01 to parquet, then its trades against Tardis
loader_check:
	$(PY) -m s2fb.cryptostruct 2026-09-01 tt
	$(PY) -m s2fb.cryptostruct 2026-09-01 depth
	$(PY) -m s2fb.crosscheck 2026-09-01

# the next unit of one listed day, e.g. make next SRC=cryptostruct SYM=BTCUSDT DAY=2026-01-14
next:
	$(PY) -m s2fb.run $(SRC) $(SYM) $(DAY) next

status:
	$(PY) -m s2fb.run $(SRC) $(SYM) $(DAY) status

verify:
	cd .. && python3 -m claimcheck $(notdir $(CURDIR))

.PHONY: env test test_slow loader_check next status verify
