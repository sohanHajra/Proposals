import json
import pytest

from s2fb import run, days
from s2fb.guard import check_day_allowed, Refused


def test_only_listed_days():
    assert check_day_allowed("2026-09-01", "BTCUSDT", "cryptostruct") == "build"
    assert check_day_allowed("2026-01-14", "BTCUSDT", "cryptostruct") == "test"
    assert check_day_allowed("2026-07-06", "BTCUSDT", "cryptostruct") == "stress"
    assert check_day_allowed("2026-11-15", "BTCUSDT", "cryptostruct") == "extra_recent"
    assert check_day_allowed("2025-03-01", "ETHUSDT", "tardis") == "first_of_month_eth"
    assert check_day_allowed("2026-06-18", "BTCUSDT", "bybit") == "bybit"
    for bad in [("2026-06-17", "BTCUSDT", "cryptostruct"), ("2026-10-01", "BTCUSDT", "tardis"),
                ("2026-01-14", "ETHUSDT", "cryptostruct"), ("2026-11-16", "BTCUSDT", "cryptostruct")]:
        with pytest.raises(Refused):
            check_day_allowed(*bad)


def test_twelve_test_days_are_wednesdays_or_the_june_thursday():
    import datetime as dt
    wd = {d: dt.date.fromisoformat(d).weekday() for d in days.TEST_DAYS}
    assert len(days.TEST_DAYS) == 12
    assert all(v == 2 for d, v in wd.items() if d != "2026-06-18") and wd["2026-06-18"] == 3


def _fake(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "RESULTS", tmp_path)
    monkeypatch.setattr(run, "DERIVED", tmp_path / "derived")
    monkeypatch.setattr(run, "s2f_unchanged", lambda: True)
    monkeypatch.setattr(run, "md5_ok", lambda *a: True)
    calls = []

    def fake_unit(source, sym, day, unit):
        calls.append(unit)
        if unit == "audit":
            return dict(gap_rule=dict(left_out=day == "2026-02-18"))
        return {}
    monkeypatch.setattr(run, "do_unit", fake_unit)
    return calls


def test_units_in_order_and_never_twice(tmp_path, monkeypatch):
    calls = _fake(tmp_path, monkeypatch)
    for _ in run.units("cryptostruct", "BTCUSDT", "2026-01-14"):
        run.run_next("cryptostruct", "BTCUSDT", "2026-01-14")
    assert calls == ["convert_tt", "convert_depth", "audit", "c1", "c2_after", "c2_before", "c2"]
    with pytest.raises(Refused):
        run.run_next("cryptostruct", "BTCUSDT", "2026-01-14")


def test_gap_rule_stops_the_day(tmp_path, monkeypatch):
    calls = _fake(tmp_path, monkeypatch)
    for _ in range(3):
        run.run_next("cryptostruct", "BTCUSDT", "2026-02-18")
    a = json.loads(run.unit_file("cryptostruct", "BTCUSDT", "2026-02-18", "test", "audit").read_text())
    assert a["gap_rule"]["left_out"] is True
    with pytest.raises(Refused):
        run.run_next("cryptostruct", "BTCUSDT", "2026-02-18")


def test_eth_waits_for_every_btc_test_day(tmp_path, monkeypatch):
    _fake(tmp_path, monkeypatch)
    with pytest.raises(Refused, match="ETHUSDT waits"):
        run.run_next("tardis", "ETHUSDT", "2025-03-01")
    for d in days.TEST_DAYS[:-1]:
        for _ in run.units("cryptostruct", "BTCUSDT", d):
            try:
                run.run_next("cryptostruct", "BTCUSDT", d)
            except Refused:
                break
    with pytest.raises(Refused, match="2026-11-18"):
        run.run_next("tardis", "ETHUSDT", "2025-03-01")
    for _ in run.units("cryptostruct", "BTCUSDT", "2026-11-18"):
        run.run_next("cryptostruct", "BTCUSDT", "2026-11-18")
    run.run_next("tardis", "ETHUSDT", "2025-03-01")      # now allowed


def test_eth_build_day_has_threshold_unit():
    assert "threshold" in run.units("tardis", "ETHUSDT", "2026-09-01")
    assert "threshold" not in run.units("tardis", "ETHUSDT", "2025-03-01")


def test_bybit_threshold_units():
    assert run.units("bybit", "BTCUSDT", "2026-09-01")[-2:] == ["threshold", "c1_own"]
    u = run.units("bybit", "BTCUSDT", "2026-01-14")
    assert "threshold" not in u and u.index("c1_frozen") == u.index("c1") + 1
    assert "c1_frozen" not in run.units("cryptostruct", "BTCUSDT", "2026-01-14")


def test_bybit_threshold_choice(tmp_path, monkeypatch):
    from s2f.signals import frozen_threshold
    f = tmp_path / "b.json"
    f.write_text('{"threshold_abs_imbalance": 0.5}')
    monkeypatch.setattr(run, "BYBIT_FILE", f)
    fz = frozen_threshold()
    assert run.threshold_and_size("BTCUSDT", "cryptostruct", "c1", "2026-01-14")[0] == fz
    assert run.threshold_and_size("BTCUSDT", "bybit", "c1", "2026-01-14")[0] == 0.5
    assert run.threshold_and_size("BTCUSDT", "bybit", "c1_frozen", "2026-01-14")[0] == fz
    assert run.threshold_and_size("BTCUSDT", "bybit", "c1", "2026-09-01")[0] == fz
    assert run.threshold_and_size("BTCUSDT", "bybit", "c1_own", "2026-09-01")[0] == 0.5


def test_loads_outside_the_runner_refused():
    from s2fb.guard import check_load_allowed, runner
    assert check_load_allowed("2026-09-01", "BTCUSDT", "cryptostruct") == "build"
    with pytest.raises(Refused, match="only through"):
        check_load_allowed("2026-01-14", "BTCUSDT", "cryptostruct")
    from s2fb import load, cryptostruct, bybit
    for f in (lambda: load.prep("cryptostruct", "2026-01-14"), lambda: cryptostruct.convert_tt("2026-01-14"),
              lambda: cryptostruct.convert_depth("2026-01-14"), lambda: bybit.convert("2026-01-14")):
        with pytest.raises(Refused, match="only through"):
            f()
    with runner():
        assert check_load_allowed("2026-01-14", "BTCUSDT", "cryptostruct") == "test"
    with pytest.raises(Refused):
        check_load_allowed("2026-01-14", "BTCUSDT", "cryptostruct")


def test_env_folders_refused_for_test_days(tmp_path, monkeypatch):
    _fake(tmp_path, monkeypatch)
    monkeypatch.setenv("S2FB_RESULTS", str(tmp_path))
    with pytest.raises(Refused, match="S2FB_"):
        run.run_next("cryptostruct", "BTCUSDT", "2026-01-14")


def test_md5_against_manifest(tmp_path, monkeypatch):
    from s2fb import cryptostruct
    assert run.manifest_md5("binance_swap-BTCUSDT-2026-01-14.txt.zst") == "29daadbe420684f39bc9b4b9b16b4075"
    assert len([d for d in days.TEST_DAYS if run.manifest_md5(f"binance_swap-BTCUSDT-{d}.txt.zst")]) == 12
    f = tmp_path / "binance_swap-BTCUSDT-2026-01-14.txt.zst"
    monkeypatch.setattr(cryptostruct, "raw_file", lambda day, sym="BTCUSDT": f)
    with pytest.raises(Refused, match="not copied"):
        run.md5_ok("cryptostruct", "BTCUSDT", "2026-01-14")
    f.write_bytes(b"not the file")
    with pytest.raises(Refused, match="differs"):
        run.md5_ok("cryptostruct", "BTCUSDT", "2026-01-14")
    assert run.md5_ok("cryptostruct", "BTCUSDT", "2026-09-01")


def test_leave_out_counts_for_eth_wait(tmp_path, monkeypatch):
    _fake(tmp_path, monkeypatch)
    run.leave_out("cryptostruct", "BTCUSDT", "2026-03-18", "MD5 mismatch")
    a = json.loads(run.unit_file("cryptostruct", "BTCUSDT", "2026-03-18", "test", "audit").read_text())
    assert a["gap_rule"]["left_out"] and "file failed" in a["gap_rule"]["reason"]
    assert "2026-03-18" not in run.btc_tests_done()
    with pytest.raises(Refused):
        run.run_next("cryptostruct", "BTCUSDT", "2026-03-18")
    with pytest.raises(Refused):
        run.leave_out("cryptostruct", "BTCUSDT", "2026-03-18", "again")
