import math


def safe_log(n):
    """Return log(n), or None if n is invalid for logarithms."""
    try:
        if n <= 0:
            return None
        return math.log(n)
    except (TypeError, ValueError, OverflowError):
        return None
