"""Stops any load of a day that 01.b does not list, and any load of a day but 2026-09-01 outside the runner."""
from contextlib import contextmanager

from .days import BUILD_DAY, BUILD, role


class Refused(Exception):
    pass


_IN_RUNNER = [False]


@contextmanager
def runner():
    """Set by s2fb.run around one unit. Only then may a day other than 2026-09-01 be read."""
    _IN_RUNNER[0] = True
    try:
        yield
    finally:
        _IN_RUNNER[0] = False


def check_day_allowed(day, sym, source):
    if day == BUILD_DAY and (source, sym) in BUILD:
        return "build"
    r = role(source, sym, day)
    if r is None:
        raise Refused(f"{source} {sym} {day} is not a day 01.b lists")
    return r


def check_load_allowed(day, sym, source):
    """For the converters and the loader (Deviation of 2026-11-23, afternoon, item 1)."""
    r = check_day_allowed(day, sym, source)
    if r != "build" and not _IN_RUNNER[0]:
        raise Refused(f"{source} {sym} {day} is read only through python -m s2fb.run")
    return r
