"""Download raw data. Usage: python -m s2f.get_data dev|test|lobster

Test days are locked until PREREGISTRATION.md exists in git history.
"""
import subprocess, sys, urllib.request, zipfile
from .paths import RAW, ROOT

TARDIS = "https://datasets.tardis.dev/v1/binance-futures/{dtype}/{y}/{m}/{d}/{sym}.csv.gz"
DTYPES = ["trades", "book_ticker", "book_snapshot_5"]
DEV_DAYS = ["2026-09-01"]
TEST_DAYS = ["2026-10-01", "2026-11-01"]
# Registered 2026-11-19 before any download. Secondary breadth check, run after the registered tests.
BREADTH_DAYS = ["2026-03-01", "2026-04-01", "2026-05-01", "2026-06-01", "2026-07-01", "2026-08-01"]
LOBSTER = "https://php.lobsterdata.com/info/sample/LOBSTER_SampleFile_{t}_2012-06-21_10.zip"
TICKERS = ["AAPL", "AMZN", "GOOG", "INTC", "MSFT"]


def _fetch(url, dest):
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print("GET", url)
    urllib.request.urlretrieve(url, dest)


def tardis(days, sym="BTCUSDT"):
    for day in days:
        y, m, d = day.split("-")
        for dt in DTYPES:
            _fetch(TARDIS.format(dtype=dt, y=y, m=m, d=d, sym=sym),
                   RAW / "tardis" / f"binance-futures_{dt}_{day}_{sym}.csv.gz")


def lobster():
    for t in TICKERS:
        z = RAW / "lobster" / f"{t}_10.zip"
        _fetch(LOBSTER.format(t=t), z)
        if not zipfile.is_zipfile(z):  # main site returns an HTML shell with HTTP 200
            z.unlink()
            raise RuntimeError(f"{t}: got HTML, not a zip; LOBSTER host changed again")
        zipfile.ZipFile(z).extractall(z.parent)


def prereg_committed() -> bool:
    r = subprocess.run(["git", "log", "--format=%H", "--", "PREREGISTRATION.md"],
                       cwd=ROOT, capture_output=True, text=True)
    return bool(r.stdout.strip())


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "dev":
        tardis(DEV_DAYS)
    elif what == "test":
        if not prereg_committed():
            sys.exit("Refusing: commit PREREGISTRATION.md before touching test days.")
        tardis(TEST_DAYS)
    elif what == "breadth":
        if not prereg_committed():
            sys.exit("Refusing: commit PREREGISTRATION.md before touching breadth days.")
        tardis(BREADTH_DAYS)
    elif what == "lobster":
        lobster()
