"""Stops any load of a day that 01.b does not list."""
from .days import BUILD_DAY, BUILD, role


class Refused(Exception):
    pass


def check_day_allowed(day, sym, source):
    if day == BUILD_DAY and (source, sym) in BUILD:
        return "build"
    r = role(source, sym, day)
    if r is None:
        raise Refused(f"{source} {sym} {day} is not a day 01.b lists")
    return r
