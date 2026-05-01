# Math Gang Collatz Experiment

Local-only Flask application for exploring Collatz dynamics, especially the odd-only map

```text
T(n) = (3n + 1) / 2^v
```

where `v = v2(3n + 1)` is the exponent of 2 dividing `3n + 1`.

The project is built as a mathematical exploration workbench. It serves a browser UI from a local Flask backend, exposes JSON endpoints for analysis, and renders local charts without external hosting.

## What This Project Does

The app investigates several Collatz questions:

- How are `v` values distributed over odd integers?
- What is the average log-space drift `log(3) - v log(2)`?
- Do residue classes modulo `m` have different drift behavior?
- How do residue classes transition under the odd-only Collatz map?
- How long does it take to encounter strong contraction events?
- What do cumulative drift paths look like?
- How long are consecutive expansion runs where `v = 1`?
- What are the empirical transition probabilities `P(v_next | v_current)`?

The UI groups tools into three categories:

- **Static**: distribution and residue summaries.
- **Dynamic**: transition maps and transition matrices.
- **Temporal**: trajectories, waiting times, cumulative drift paths, and expansion runs.

## Project Structure

```text
math-gang-collatz-experiment/
  backend/
    app.py              Flask app and API routes
    collatz.py          Core Collatz functions
    analysis.py         Statistical and trajectory analysis functions
    utils.py            Utility helpers
  frontend/
    index.html          Local browser UI
    css/styles.css      UI styling
    js/main.js          API calls, chart rendering, copy/export behavior
    js/lib/chart.min.js Local chart library file
  requirements.txt
  launch_math_gang.bat
  sync_github.bat
  README.md
```

## Requirements

- Python 3
- Flask
- NumPy
- pandas
- A modern browser

Everything runs locally. No external hosting is required.

## Windows 11 Local Setup

### 1. Install Python

Install Python 3 from one of these sources:

- Microsoft Store
- python.org
- your company software portal

During install, enable **Add Python to PATH** if available.

Check Python:

```powershell
py -3 --version
```

If `py -3` works, use it for the commands below. If your system has `python` configured normally, `python` also works.

### 2. Get the Project

If Git is installed:

```powershell
git clone https://github.com/monte1gm/math-gang-collatz-experiment.git
cd math-gang-collatz-experiment
```

If Git is not installed, download the GitHub ZIP, extract it, then open PowerShell in the extracted folder.

### 3. Create a Virtual Environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation for this session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run the App

```powershell
python backend\app.py
```

Open:

```text
http://localhost:5000/app
```

### Windows Shortcut

This repo includes:

```text
launch_math_gang.bat
```

You can double-click it or run:

```powershell
.\launch_math_gang.bat
```

It installs requirements, starts Flask, and opens the browser.

## macOS Local Setup

### 1. Install Python

Use either Homebrew or python.org.

With Homebrew:

```bash
brew install python git
```

Check Python:

```bash
python3 --version
```

### 2. Get the Project

```bash
git clone https://github.com/monte1gm/math-gang-collatz-experiment.git
cd math-gang-collatz-experiment
```

If you do not use Git, download the GitHub ZIP, extract it, and open Terminal in the extracted folder.

### 3. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run the App

```bash
python backend/app.py
```

Open:

```text
http://localhost:5000/app
```

or from Terminal:

```bash
open http://localhost:5000/app
```

## Using the UI

After opening `http://localhost:5000/app`, choose one panel, adjust the inputs, and run the analysis.

The output area shows JSON. The chart area renders a local visualization when the response has chartable data.

Available copy/export controls:

- **Copy JSON**: copies the visible JSON output.
- **Copy Chart Data**: copies the data used for the current chart.
- **Copy Chart Image**: copies the chart canvas as an image when browser clipboard permissions allow it.

The chart legend below the graph maps line colors back to series labels. For large multi-series results, the chart shows a limited number of series and the copied chart data keeps the full result.

## Analysis Panels

### Static

**v Distribution and Drift**

Samples odd integers and computes:

- histogram of `v`
- probability distribution of `v`
- mean log-space drift
- autocorrelation at chosen lags

**Residue-Class Drift**

Groups odd sampled integers by `n mod m` and computes:

- count per residue
- mean `v`
- drift by residue
- high-v event frequency

### Dynamic

**Residue Transitions**

Computes how each odd residue class maps under:

```text
T(n) = (3n + 1) / 2^v
```

It returns one-step and multi-step residue paths.

**v Transition Matrix**

Estimates empirical transition probabilities:

```text
P(v_{k+1} | v_k)
```

from sampled trajectories.

### Temporal

**Trajectory**

Computes:

- full standard Collatz trajectory
- odd-only trajectory
- log path
- deltas
- aligned `v` sequence
- summary metrics

**Time to v Threshold**

Measures how many odd-only steps it takes to first encounter:

```text
v >= threshold
```

**Cumulative Drift**

Tracks:

```text
S_k = sum(log(3) - v_k log(2))
```

along odd-only steps.

**Expansion Run Lengths**

Measures consecutive runs of:

```text
v = 1
```

These are pure odd-only expansion steps.

## API Endpoints

All endpoints are local under:

```text
http://localhost:5000
```

### Health

```text
GET /health
```

Returns:

```json
{"status": "ok"}
```

### Trajectory

```text
GET /api/trajectory?n=27
```

### v Distribution and Drift

```text
GET /api/v-analysis?start=1&count=10000&max_v=10&lag1=1&lag2=2
```

### Residue-Class Drift

```text
GET /api/residue-analysis?start=1&mod=16&count=20000&threshold=3
```

### Residue Transitions

```text
GET /api/transitions?mod=16&steps=5
```

### Time to v Threshold

```text
GET /api/time-to-v?start=1&threshold=3&count=5000
```

### v Transition Matrix

```text
GET /api/v-transitions?start=1&count=5000&max_steps=100&max_v=10
```

### Cumulative Drift

```text
GET /api/drift-trajectories?start=1&count=100&max_steps=200
```

### Expansion Run Lengths

```text
GET /api/expansion-runs?start=1&count=5000&max_steps=200
```

## Local Limits

The backend caps some inputs to keep responses manageable:

- `v-analysis` count: capped at `1,000,000`
- `residue-analysis` count: capped at `1,000,000`
- `time-to-v` count: capped at `10,000`
- `v-transitions` count: capped at `10,000`
- `v-transitions` max steps: capped at `1,000`
- `drift-trajectories` count: capped at `500`
- `drift-trajectories` max steps: capped at `2,000`
- `expansion-runs` count: capped at `10,000`
- `expansion-runs` max steps: capped at `2,000`

## Chart.js Note

The project expects a local chart script at:

```text
frontend/js/lib/chart.min.js
```

This keeps the app local-only and avoids CDN dependencies. The repo currently includes a lightweight local fallback with a Chart.js-compatible interface for the charts used by this app. You can replace it with the official Chart.js `chart.min.js` file if desired.

## GitHub Sync

If Git is installed normally:

```bash
git status
git add .
git commit -m "Update project"
git push
```

On the original Windows machine used for this project, portable Git was placed under `.tools/` because system Git was not available. That local folder is intentionally ignored by Git.

That machine also has:

```text
sync_github.bat
```

Run:

```powershell
.\sync_github.bat "Update README"
```

to stage, commit, and push changes using the local portable Git setup.

## Troubleshooting

### `git` is not recognized

Install Git for your operating system, or use the portable Git path if this is the original Windows project folder:

```powershell
.\.tools\mingit\cmd\git.exe status
```

### `python` opens the Microsoft Store on Windows

Use:

```powershell
py -3 backend\app.py
```

or disable the Microsoft Store Python alias in Windows App Execution Aliases.

### PowerShell will not activate `.venv`

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Port 5000 is already in use

Stop the other local process using port 5000, or change the port in `backend/app.py`:

```python
app.run(host="localhost", port=5000, debug=True)
```

### Browser does not show latest UI

Hard refresh:

```text
Ctrl+F5
```

On macOS:

```text
Cmd+Shift+R
```

## Development Notes

- Backend is intentionally simple Flask.
- CORS headers are added manually.
- No external hosting is required.
- The frontend is plain HTML, CSS, and JavaScript.
- API responses are JSON serializable.
- This project is exploratory and intended for local mathematical experimentation, not production deployment.
