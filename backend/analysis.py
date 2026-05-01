import math

import numpy as np

from backend.collatz import v2


def compute_log_path(trajectory):
    """
    Convert trajectory into log-space.
    Returns list of floats.
    """
    return [math.log(n) for n in trajectory]


def compute_deltas(log_path):
    """
    Compute delta x = x_{k+1} - x_k.
    """
    return [
        log_path[i + 1] - log_path[i]
        for i in range(len(log_path) - 1)
    ]


def extract_v_sequence(trajectory):
    """
    Compute v_k for each step where n is odd.

    v_k is the exponent of 2 dividing (3n + 1).
    For even steps, return None to preserve alignment.
    """
    vs = []

    for n in trajectory[:-1]:
        if n % 2 == 0:
            vs.append(None)
        else:
            vs.append(v2(3 * n + 1))

    return vs


def summarize_trajectory(trajectory):
    """
    Compute key metrics.
    """
    if not trajectory:
        return {}

    peak_value = max(trajectory)
    peak_index = trajectory.index(peak_value)

    return {
        "length": len(trajectory),
        "peak_value": peak_value,
        "time_to_peak": peak_index,
        "stopping_time": len(trajectory) - 1,
    }


def sample_v_values(start, count):
    """
    Sample v(n) over odd integers:
    n = start, start + 2, start + 4, ...
    """
    values = []
    n = start if start % 2 == 1 else start + 1

    for _ in range(count):
        val = 3 * n + 1
        values.append(v2(val))
        n += 2

    return np.array(values)


def compute_v_distribution(vs, max_k=10):
    """
    Return histogram counts for v = 1..max_k.

    Values greater than max_k are included in the max_k bucket.
    """
    hist = {k: 0 for k in range(1, max_k + 1)}
    total = len(vs)

    if total == 0:
        return {
            "counts": hist,
            "probabilities": {k: 0 for k in hist},
            "total": 0,
        }

    for v in vs:
        key = int(v)
        if key <= max_k:
            hist[key] += 1
        else:
            hist[max_k] += 1

    probs = {
        k: hist[k] / total
        for k in hist
    }

    return {
        "counts": hist,
        "probabilities": probs,
        "total": total,
    }


def compute_drift(vs):
    """
    Compute mean drift in log-space.
    """
    if len(vs) == 0:
        return None

    steps = np.log(3) - vs * np.log(2)
    return float(np.mean(steps))


def compute_autocorrelation(vs, lag=1):
    """
    Simple autocorrelation for v sequence.
    """
    if len(vs) <= lag:
        return None

    v1 = vs[:-lag]
    v2_shifted = vs[lag:]

    if len(v1) < 2 or np.std(v1) == 0 or np.std(v2_shifted) == 0:
        return None

    corr = np.corrcoef(v1, v2_shifted)[0, 1]

    if np.isnan(corr):
        return None

    return float(corr)


def drift_by_mod(start, count, mod):
    """
    Compute drift grouped by n % mod.
    Only considers odd n.
    """
    buckets = {r: [] for r in range(mod)}
    n = start if start % 2 == 1 else start + 1

    for _ in range(count):
        r = n % mod
        v = v2(3 * n + 1)
        buckets[r].append(v)
        n += 2

    results = {}

    for r, vs in buckets.items():
        if len(vs) == 0:
            continue

        vs_arr = np.array(vs)
        drift = float(np.mean(np.log(3) - vs_arr * np.log(2)))

        results[r] = {
            "count": len(vs),
            "mean_v": float(np.mean(vs_arr)),
            "drift": drift,
        }

    return results


def high_v_frequency_by_mod(start, count, mod, threshold=3):
    """
    Frequency of large v events (v >= threshold) by residue class.
    """
    buckets = {r: {"total": 0, "high": 0} for r in range(mod)}
    n = start if start % 2 == 1 else start + 1

    for _ in range(count):
        r = n % mod
        v = v2(3 * n + 1)

        buckets[r]["total"] += 1
        if v >= threshold:
            buckets[r]["high"] += 1

        n += 2

    results = {}

    for r, data in buckets.items():
        if data["total"] == 0:
            continue

        results[r] = {
            "frequency": data["high"] / data["total"],
            "total": data["total"],
        }

    return results


def transition_table_mod(mod):
    """
    Compute deterministic transitions:
    r -> T(r) mod mod

    Only for odd residues r.
    """
    table = {}

    for r in range(mod):
        if r % 2 == 0:
            continue

        n = r
        v = v2(3 * n + 1)
        t = (3 * n + 1) // (2 ** v)

        table[r] = {
            "next_residue": t % mod,
            "v": v,
        }

    return table


def multi_step_transitions(mod, steps=5):
    """
    Track multi-step transitions for each residue.
    """
    results = {}

    for r in range(mod):
        if r % 2 == 0:
            continue

        path = []
        n = r

        for _ in range(steps):
            v = v2(3 * n + 1)
            n = (3 * n + 1) // (2 ** v)

            path.append({
                "n": n,
                "residue": n % mod,
                "v": v,
            })

        results[r] = path

    return results


def time_to_threshold_v(n, threshold):
    """
    Return number of odd-only steps until v >= threshold.
    """
    steps = 0

    while n != 1:
        if n % 2 == 0:
            n //= 2
            continue

        v = v2(3 * n + 1)

        if v >= threshold:
            return steps

        n = (3 * n + 1) // (2 ** v)
        steps += 1

    return None


def sample_time_to_threshold(start, count, threshold):
    """
    Sample time-to-threshold over many starting values.
    """
    results = []
    n = start

    for _ in range(count):
        t = time_to_threshold_v(n, threshold)
        if t is not None:
            results.append(t)
        n += 1

    return results


def v_transition_matrix(start, count, max_steps=100, max_v=10):
    """
    Build transition counts between successive v values.
    """
    matrix = {
        i: {j: 0 for j in range(1, max_v + 1)}
        for i in range(1, max_v + 1)
    }

    total_transitions = {
        i: 0 for i in range(1, max_v + 1)
    }

    for n0 in range(start, start + count):
        n = n0
        prev_v = None
        steps = 0

        while n != 1 and steps < max_steps:
            if n % 2 == 0:
                n //= 2
                continue

            v = v2(3 * n + 1)
            v_capped = min(v, max_v)

            if prev_v is not None:
                matrix[prev_v][v_capped] += 1
                total_transitions[prev_v] += 1

            prev_v = v_capped
            n = (3 * n + 1) // (2 ** v)
            steps += 1

    prob_matrix = {}

    for i in matrix:
        total = total_transitions[i]
        if total == 0:
            continue

        prob_matrix[i] = {
            j: matrix[i][j] / total
            for j in matrix[i]
        }

    return {
        "counts": matrix,
        "probabilities": prob_matrix,
        "totals": total_transitions,
    }


def drift_trajectory(n, max_steps=200):
    """
    Compute cumulative drift trajectory for a single starting value.
    Returns list of cumulative sums S_k.
    """
    drift_path = []
    cumulative = 0.0
    steps = 0

    while n != 1 and steps < max_steps:
        if n % 2 == 0:
            n //= 2
            continue

        v = v2(3 * n + 1)
        delta = math.log(3) - v * math.log(2)
        cumulative += delta

        drift_path.append(cumulative)

        n = (3 * n + 1) // (2 ** v)
        steps += 1

    return drift_path


def sample_drift_trajectories(start, count, max_steps=200):
    """
    Sample multiple drift trajectories.
    """
    results = {}

    for n in range(start, start + count):
        path = drift_trajectory(n, max_steps)
        if path:
            results[n] = path

    return results


def expansion_run_lengths(n, max_steps=200):
    """
    Compute lengths of consecutive runs of v = 1 for a single trajectory.
    Returns a list of run lengths.
    """
    runs = []
    current_run = 0
    steps = 0

    while n != 1 and steps < max_steps:
        if n % 2 == 0:
            n //= 2
            continue

        v = v2(3 * n + 1)

        if v == 1:
            current_run += 1
        else:
            if current_run > 0:
                runs.append(current_run)
                current_run = 0

        n = (3 * n + 1) // (2 ** v)
        steps += 1

    if current_run > 0:
        runs.append(current_run)

    return runs


def sample_expansion_runs(start, count, max_steps=200):
    """
    Sample expansion run lengths across many trajectories.
    """
    all_runs = []

    for n in range(start, start + count):
        runs = expansion_run_lengths(n, max_steps)
        all_runs.extend(runs)

    return all_runs
