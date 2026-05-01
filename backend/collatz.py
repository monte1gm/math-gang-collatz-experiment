def v2(n):
    """Return the exponent of 2 dividing n."""
    if n == 0:
        raise ValueError("v2 is undefined for 0")

    n = abs(n)
    exponent = 0

    while n % 2 == 0:
        exponent += 1
        n //= 2

    return exponent


def collatz_step(n):
    """Return the next value in the standard Collatz sequence."""
    if n < 1:
        raise ValueError("n must be a positive integer")

    if n % 2 == 0:
        return n // 2

    return 3 * n + 1


def collatz_trajectory(n):
    """Return the full Collatz trajectory from n down to 1."""
    if n < 1:
        raise ValueError("n must be a positive integer")

    trajectory = [n]

    while n != 1:
        n = collatz_step(n)
        trajectory.append(n)

    return trajectory


def collatz_odd_step(n):
    """Return T(n) = (3n + 1) / 2^v for odd n."""
    if n < 1:
        raise ValueError("n must be a positive integer")
    if n % 2 == 0:
        raise ValueError("n must be odd")

    value = 3 * n + 1
    return value // (2 ** v2(value))


def collatz_odd_trajectory(n):
    """Return the odd-only Collatz trajectory from odd n down to 1."""
    if n < 1:
        raise ValueError("n must be a positive integer")
    if n % 2 == 0:
        raise ValueError("n must be odd")

    trajectory = [n]

    while n != 1:
        n = collatz_odd_step(n)
        trajectory.append(n)

    return trajectory
