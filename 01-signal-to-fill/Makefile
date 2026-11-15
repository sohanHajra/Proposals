PY := .venv/bin/python
export PYTHONPATH := src

env:
	uv venv .venv --python 3.12 && uv pip install -r requirements.lock --python $(PY)

data:
	$(PY) -m s2f.get_data dev && $(PY) -m s2f.get_data lobster

audit:
	$(PY) -m s2f.data_audit 2026-09-01
	$(PY) -m s2f.lobster_audit

test:
	$(PY) -m pytest -q tests

reproduce: env data audit test
