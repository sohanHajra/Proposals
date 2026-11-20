from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get("S2F_DATA", ROOT / "data"))
RAW = DATA / "raw"
RESULTS = ROOT / "results"

DEV_DAY = "2026-09-01"


def result_path(sub, stem, day, root=None):
    """results/<sub>/<stem>_dev_<day>.json on the dev day, results/<sub>/<stem>_<day>.json on any other."""
    base = (RESULTS if root is None else Path(root)) / sub
    return base / (f"{stem}_dev_{day}.json" if day == DEV_DAY else f"{stem}_{day}.json")


def guard_day(day):
    """Stop unless this is the dev day or a test day run was started on purpose."""
    if day != DEV_DAY and os.environ.get("S2F_ALLOW_TEST_DAY") != "1":
        raise SystemExit("dev day only until the test day run is started on purpose")


def float_prices(path):
    """Every price and amount column of a Tardis csv read as Float64. On some days the first rows
    carry whole number prices, so polars would otherwise guess an integer column and stop at the
    first decimal. On the dev and test days these columns were already read as Float64."""
    import gzip
    import polars as pl
    with gzip.open(path, "rt") as f:
        head = f.readline().strip().split(",")
    return {c: pl.Float64 for c in head if "price" in c or "amount" in c}
