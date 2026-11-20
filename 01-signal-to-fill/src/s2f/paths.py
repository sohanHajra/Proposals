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
