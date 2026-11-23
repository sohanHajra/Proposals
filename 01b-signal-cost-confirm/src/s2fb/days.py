"""Every day 01.b may use, as listed in PREREGISTRATION.md (b81f5f6 and the Deviation of 2026-11-22).
Nothing outside these lists is loaded."""

BUILD_DAY = "2026-09-01"

# CryptoStruct Binance USDT-M BTCUSDT, the Wednesday closest to the 15th, 2026-06-17 replaced by 2026-06-18
TEST_DAYS = ("2025-12-17", "2026-01-14", "2026-02-18", "2026-03-18", "2026-04-15", "2026-05-13",
             "2026-06-18", "2026-07-15", "2026-08-12", "2026-09-16", "2026-10-14", "2026-11-18")

# CryptoStruct free samples, each reported alone and never in a verdict
STRESS_DAY = "2026-07-06"
EXTRA_RECENT_DAYS = ("2026-11-13", "2026-11-14", "2026-11-15")

# Tardis free first of month days not used in 01
FIRST_OF_MONTH = ("2025-03-01", "2025-04-01", "2025-05-01", "2025-06-01", "2025-07-01", "2025-08-01",
                  "2025-09-01", "2025-10-01", "2025-11-01", "2025-12-01", "2026-01-01", "2026-02-01")

# (source, symbol) -> (role, days). Each role is reported on its own.
PLAN = {
    ("cryptostruct", "BTCUSDT"): {"test": TEST_DAYS, "stress": (STRESS_DAY,), "extra_recent": EXTRA_RECENT_DAYS},
    ("tardis", "BTCUSDT"): {"first_of_month": FIRST_OF_MONTH},
    ("tardis", "ETHUSDT"): {"first_of_month_eth": FIRST_OF_MONTH},
    ("bybit", "BTCUSDT"): {"bybit": TEST_DAYS},
}

# what may be loaded on the build day to build each source (2026-09-01 only)
BUILD = {("cryptostruct", "BTCUSDT"), ("tardis", "BTCUSDT"), ("tardis", "ETHUSDT"), ("bybit", "BTCUSDT")}


def role(source, sym, day):
    """The role of a listed day, or None if the day is not listed for that source and symbol."""
    for r, days in PLAN.get((source, sym), {}).items():
        if day in days:
            return r
    return None
