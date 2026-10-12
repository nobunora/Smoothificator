"""One owner of finite IEEE-754 binary64 numeric validation."""
from math import isfinite


def finite_binary64(value: object) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return isfinite(float(value))
    except (OverflowError, ValueError):
        return False
