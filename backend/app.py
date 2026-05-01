from pathlib import Path
import sys

from flask import Flask, jsonify, make_response, request, send_from_directory


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.analysis import (
    compute_autocorrelation,
    compute_deltas,
    compute_drift,
    compute_log_path,
    compute_v_distribution,
    drift_by_mod,
    extract_v_sequence,
    high_v_frequency_by_mod,
    multi_step_transitions,
    sample_expansion_runs,
    sample_v_values,
    sample_drift_trajectories,
    sample_time_to_threshold,
    summarize_trajectory,
    transition_table_mod,
    v_transition_matrix,
)
from backend.collatz import collatz_odd_trajectory, collatz_trajectory


app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path="",
)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/")
def backend_home():
    return "Math Gang Backend Running"


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/trajectory")
def api_trajectory():
    try:
        n = int(request.args.get("n", "0"))
        if n < 1:
            raise ValueError("n must be positive")

        trajectory = collatz_trajectory(n)

        odd_trajectory = (
            collatz_odd_trajectory(n)
            if n % 2 == 1
            else []
        )

        log_path = compute_log_path(trajectory)
        deltas = compute_deltas(log_path)
        v_sequence = extract_v_sequence(trajectory)
        summary = summarize_trajectory(trajectory)

        return jsonify({
            "input": n,
            "trajectory": trajectory,
            "odd_trajectory": odd_trajectory,
            "log_path": log_path,
            "deltas": deltas,
            "v_sequence": v_sequence,
            "summary": summary,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/v-analysis")
def api_v_analysis():
    try:
        start = int(request.args.get("start", "1"))
        count = int(request.args.get("count", "10000"))
        max_v = int(request.args.get("max_v", "10"))
        lag1 = int(request.args.get("lag1", "1"))
        lag2 = int(request.args.get("lag2", "2"))

        if start < 1:
            raise ValueError("start must be positive")

        if count < 1:
            raise ValueError("count must be positive")

        if max_v < 1:
            raise ValueError("max_v must be positive")

        if lag1 < 1 or lag2 < 1:
            raise ValueError("lags must be positive")

        if count > 1_000_000:
            count = 1_000_000

        if max_v > 100:
            max_v = 100

        vs = sample_v_values(start, count)

        dist = compute_v_distribution(vs, max_k=max_v)
        drift = compute_drift(vs)
        ac1 = compute_autocorrelation(vs, lag=lag1)
        ac2 = compute_autocorrelation(vs, lag=lag2)

        return jsonify({
            "start": start,
            "count": count,
            "max_v": max_v,
            "distribution": dist,
            "drift": drift,
            "autocorrelation": {
                f"lag{lag1}": ac1,
                f"lag{lag2}": ac2,
            },
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/residue-analysis")
def api_residue_analysis():
    try:
        start = int(request.args.get("start", "1"))
        mod = int(request.args.get("mod", "16"))
        count = int(request.args.get("count", "10000"))
        threshold = int(request.args.get("threshold", "3"))

        if start < 1:
            raise ValueError("start must be positive")

        if mod < 2:
            raise ValueError("mod must be >= 2")

        if count < 1:
            raise ValueError("count must be positive")

        if threshold < 1:
            raise ValueError("threshold must be positive")

        if count > 1_000_000:
            count = 1_000_000

        drift_data = drift_by_mod(start, count, mod)
        high_v_data = high_v_frequency_by_mod(start, count, mod, threshold=threshold)

        return jsonify({
            "start": start,
            "mod": mod,
            "count": count,
            "threshold": threshold,
            "drift_by_residue": drift_data,
            "high_v_frequency": high_v_data,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/transitions")
def api_transitions():
    try:
        mod = int(request.args.get("mod", "16"))
        steps = int(request.args.get("steps", "5"))

        if mod < 2:
            raise ValueError("mod must be >= 2")

        if steps < 1:
            raise ValueError("steps must be positive")

        if steps > 100:
            steps = 100

        table = transition_table_mod(mod)
        paths = multi_step_transitions(mod, steps=steps)

        return jsonify({
            "mod": mod,
            "steps": steps,
            "one_step": table,
            "multi_step": paths,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/time-to-v")
def api_time_to_v():
    try:
        start = int(request.args.get("start", "1"))
        threshold = int(request.args.get("threshold", "3"))
        count = int(request.args.get("count", "1000"))

        if start < 1:
            raise ValueError("start must be positive")

        if threshold < 2:
            raise ValueError("threshold must be >= 2")

        if count < 1:
            raise ValueError("count must be positive")

        if count > 10000:
            count = 10000

        times = sample_time_to_threshold(start, count, threshold)

        return jsonify({
            "start": start,
            "threshold": threshold,
            "sampled_count": count,
            "count": len(times),
            "times": times,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/v-transitions")
def api_v_transitions():
    try:
        start = int(request.args.get("start", "1"))
        count = int(request.args.get("count", "1000"))
        max_steps = int(request.args.get("max_steps", "100"))
        max_v = int(request.args.get("max_v", "10"))

        if start < 1:
            raise ValueError("start must be positive")

        if count < 1:
            raise ValueError("count must be positive")

        if max_steps < 1:
            raise ValueError("max_steps must be positive")

        if max_v < 1:
            raise ValueError("max_v must be positive")

        if count > 10000:
            count = 10000

        if max_steps > 1000:
            max_steps = 1000

        if max_v > 100:
            max_v = 100

        result = v_transition_matrix(start, count, max_steps=max_steps, max_v=max_v)

        return jsonify({
            "start": start,
            "count": count,
            "max_steps": max_steps,
            "max_v": max_v,
            **result,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/drift-trajectories")
def api_drift_trajectories():
    try:
        start = int(request.args.get("start", "1"))
        count = int(request.args.get("count", "100"))
        max_steps = int(request.args.get("max_steps", "200"))

        if start < 1:
            raise ValueError("start must be positive")

        if count < 1:
            raise ValueError("count must be positive")

        if max_steps < 1:
            raise ValueError("max_steps must be positive")

        if count > 500:
            count = 500

        if max_steps > 2000:
            max_steps = 2000

        result = sample_drift_trajectories(start, count, max_steps)

        return jsonify({
            "start": start,
            "sampled_count": count,
            "count": len(result),
            "max_steps": max_steps,
            "trajectories": result,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/expansion-runs")
def api_expansion_runs():
    try:
        start = int(request.args.get("start", "1"))
        count = int(request.args.get("count", "1000"))
        max_steps = int(request.args.get("max_steps", "200"))

        if start < 1:
            raise ValueError("start must be positive")

        if count < 1:
            raise ValueError("count must be positive")

        if max_steps < 1:
            raise ValueError("max_steps must be positive")

        if count > 10000:
            count = 10000

        if max_steps > 2000:
            max_steps = 2000

        runs = sample_expansion_runs(start, count, max_steps)

        return jsonify({
            "start": start,
            "sampled_count": count,
            "max_steps": max_steps,
            "count": len(runs),
            "runs": runs,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/app")
def frontend_app():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>", methods=["OPTIONS"])
def options(filename):
    return make_response("", 204)


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
