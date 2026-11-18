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

.PHONY: env data audit test sanity taker passive reproduce

reproduce: env data audit test sanity taker passive

taker:
	$(PY) -m s2f.taker 2026-09-01

passive:
	$(PY) -m s2f.passive 2026-09-01
