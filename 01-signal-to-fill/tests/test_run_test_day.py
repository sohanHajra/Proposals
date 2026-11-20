import json
import pytest
from s2f import run_test_day as R
from s2f.paths import result_path


@pytest.mark.parametrize("day", ["2026-09-01", "2026-12-01", "2026-10-02", "yesterday", "2025-10-01"])
def test_refuses_any_date_that_is_not_registered(day, capsys):
    assert R.main([day]) == 1
    assert "Refusing" in capsys.readouterr().err


def test_takes_exactly_one_argument():
    assert R.main([]) == 2
    assert R.main(["2026-10-01", "--seed", "1"]) == 2


def test_registered_days_and_steps():
    assert R.steps_for("2026-10-01") == R.steps_for("2026-11-01") == R.STEPS_TEST
    for d in ("2026-03-01", "2026-04-01", "2026-05-01", "2026-06-01", "2026-07-01", "2026-08-01"):
        assert R.steps_for(d) == R.STEPS_BREADTH
    assert "robustness" not in R.STEPS_BREADTH


def test_refuses_to_overwrite_an_existing_output(tmp_path, monkeypatch):
    monkeypatch.delenv("S2F_ALLOW_TEST_DAY", raising=False)
    p = result_path("taker", "taker", "2026-10-01", tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"already": "run"}))
    with pytest.raises(R.Refused, match="already exist"):
        R.run_day("2026-10-01", root=tmp_path, derived=tmp_path / "derived")
    assert json.loads(p.read_text()) == {"already": "run"}


def test_refuses_to_overwrite_saved_arrays(tmp_path, monkeypatch):
    monkeypatch.delenv("S2F_ALLOW_TEST_DAY", raising=False)
    d = tmp_path / "derived"; d.mkdir()
    (d / "passive_random_after_2026-11-01.npz").write_bytes(b"x")
    with pytest.raises(R.Refused, match="already exist"):
        R.run_day("2026-11-01", root=tmp_path / "results", derived=d)


def test_outputs_are_named_by_date_not_dev(tmp_path):
    for p in R.outputs("2026-10-01", R.STEPS_TEST, tmp_path):
        assert "2026-10-01" in p.name and "dev" not in p.name


@pytest.mark.parametrize("mod", ["taker", "passive", "sanity", "tie_share", "fixed_price", "taker_followups",
                                 "passive_followups", "jumps", "robustness"])
def test_modules_refuse_a_test_day_unless_started_on_purpose(mod, monkeypatch):
    import subprocess, sys, os
    env = {k: v for k, v in os.environ.items() if k != "S2F_ALLOW_TEST_DAY"}
    env["PYTHONPATH"] = "src"
    r = subprocess.run([sys.executable, "-m", f"s2f.{mod}", "2026-10-01", "summarize"], env=env,
                       capture_output=True, text=True, cwd=str(__import__("pathlib").Path(__file__).parents[1]))
    assert r.returncode != 0 and "dev day only" in (r.stderr + r.stdout)
