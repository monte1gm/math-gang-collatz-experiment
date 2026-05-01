const output = document.getElementById("output");
const chartCanvas = document.getElementById("chart-canvas");
const chartLegend = document.getElementById("chart-legend");
const copyJsonButton = document.getElementById("copy-json");
const copyDataButton = document.getElementById("copy-data");
const copyImageButton = document.getElementById("copy-image");

let currentChart = null;
let currentData = null;

const CHART_COLORS = [
  "#2563eb",
  "#0f766e",
  "#c2410c",
  "#7c3aed",
  "#be123c",
  "#0891b2",
  "#4d7c0f",
  "#a16207",
  "#9333ea",
  "#dc2626",
  "#0369a1",
  "#475569",
];

const controls = {
  trajectory: {
    n: document.getElementById("trajectory-input"),
    button: document.getElementById("test-api-button"),
  },
  vAnalysis: {
    start: document.getElementById("v-start-input"),
    count: document.getElementById("v-count-input"),
    maxV: document.getElementById("v-max-input"),
    lag1: document.getElementById("v-lag-1-input"),
    lag2: document.getElementById("v-lag-2-input"),
    button: document.getElementById("v-analysis-button"),
  },
  residue: {
    start: document.getElementById("residue-start-input"),
    mod: document.getElementById("residue-mod-input"),
    count: document.getElementById("residue-count-input"),
    threshold: document.getElementById("residue-threshold-input"),
    button: document.getElementById("residue-analysis-button"),
  },
  transitions: {
    mod: document.getElementById("transition-mod-input"),
    steps: document.getElementById("transition-steps-input"),
    button: document.getElementById("transitions-button"),
  },
  timeToV: {
    start: document.getElementById("time-start-input"),
    threshold: document.getElementById("time-threshold-input"),
    count: document.getElementById("time-count-input"),
    button: document.getElementById("time-to-v-button"),
  },
  driftTrajectories: {
    start: document.getElementById("drift-start-input"),
    count: document.getElementById("drift-count-input"),
    maxSteps: document.getElementById("drift-max-steps-input"),
    button: document.getElementById("drift-trajectories-button"),
  },
  expansionRuns: {
    start: document.getElementById("expansion-start-input"),
    count: document.getElementById("expansion-count-input"),
    maxSteps: document.getElementById("expansion-max-steps-input"),
    button: document.getElementById("expansion-runs-button"),
  },
  vTransitions: {
    start: document.getElementById("vt-start-input"),
    count: document.getElementById("vt-count-input"),
    maxSteps: document.getElementById("vt-max-steps-input"),
    maxV: document.getElementById("vt-max-input"),
    button: document.getElementById("v-transitions-button"),
  },
};

function valueOf(input, fallback) {
  return input.value.trim() || fallback;
}

function buildUrl(path, params) {
  return `${path}?${new URLSearchParams(params).toString()}`;
}

async function fetchJson(url) {
  const response = await fetch(url);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || `Request failed with status ${response.status}`);
  }

  return response.json();
}

async function runAnalysis(message, url, formatter = null) {
  output.textContent = message;
  currentData = null;

  try {
    const data = await fetchJson(url);
    const result = formatter ? formatter(data) : data;
    output.textContent = JSON.stringify(result, null, 2);
    renderChartForResponse(data);
  } catch (error) {
    clearChart();
    output.textContent = `Error: ${error.message}`;
  }
}

function clearChart() {
  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }
  chartLegend.replaceChildren();
}

function renderLegend(items, note = "") {
  chartLegend.replaceChildren();

  if (note) {
    const noteElement = document.createElement("div");
    noteElement.className = "legend-note";
    noteElement.textContent = note;
    chartLegend.appendChild(noteElement);
  }

  items.forEach((item) => {
    const legendItem = document.createElement("div");
    legendItem.className = "legend-item";
    legendItem.title = item.label;

    const swatch = document.createElement("span");
    swatch.className = "legend-swatch";
    swatch.style.backgroundColor = item.color;

    const label = document.createElement("span");
    label.textContent = item.label;

    legendItem.append(swatch, label);
    chartLegend.appendChild(legendItem);
  });
}

function chartOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
  };
}

function renderHistogram(dataObj, label = "Frequency") {
  if (!dataObj) {
    return;
  }

  const labels = Object.keys(dataObj);
  const values = Object.values(dataObj).map(Number);
  const color = CHART_COLORS[0];

  clearChart();

  currentChart = new Chart(chartCanvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label,
        data: values,
        backgroundColor: color,
        borderColor: color,
      }],
    },
    options: chartOptions(),
  });

  renderLegend([{ label, color }]);
  currentData = dataObj;
}

function renderLineChart(series, label = "Value") {
  if (!Array.isArray(series)) {
    return;
  }

  clearChart();
  const color = CHART_COLORS[0];

  currentChart = new Chart(chartCanvas, {
    type: "line",
    data: {
      labels: series.map((_, i) => i),
      datasets: [{
        label,
        data: series,
        borderColor: color,
        backgroundColor: color,
        fill: false,
      }],
    },
    options: chartOptions(),
  });

  renderLegend([{ label, color }]);
  currentData = series;
}

function renderMultiLineChart(seriesObj, label = "Cumulative Drift") {
  if (!seriesObj) {
    return;
  }

  const allEntries = Object.entries(seriesObj);
  const entries = allEntries.slice(0, 12);
  const maxLength = entries.reduce((max, [, series]) => Math.max(max, series.length), 0);
  const legendItems = entries.map(([key], index) => ({
    label: `${label} ${key}`,
    color: CHART_COLORS[index % CHART_COLORS.length],
  }));
  const note = allEntries.length > entries.length
    ? `Showing ${entries.length} of ${allEntries.length} series. Copy chart data for the full set.`
    : "";

  clearChart();

  currentChart = new Chart(chartCanvas, {
    type: "line",
    data: {
      labels: Array.from({ length: maxLength }, (_, i) => i),
      datasets: entries.map(([key, series], index) => ({
        label: `${label} ${key}`,
        data: series,
        borderColor: CHART_COLORS[index % CHART_COLORS.length],
        backgroundColor: CHART_COLORS[index % CHART_COLORS.length],
        fill: false,
      })),
    },
    options: chartOptions(),
  });

  renderLegend(legendItems, note);
  currentData = seriesObj;
}

function renderHeatmap(matrix) {
  if (!matrix) {
    return;
  }

  const labels = [];
  const values = [];

  for (const row in matrix) {
    for (const col in matrix[row]) {
      labels.push(`${row}->${col}`);
      values.push(Number(matrix[row][col]));
    }
  }

  clearChart();
  const color = CHART_COLORS[0];

  currentChart = new Chart(chartCanvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Transition Prob",
        data: values,
        backgroundColor: color,
        borderColor: color,
      }],
    },
    options: chartOptions(),
  });

  renderLegend([{ label: "Transition Prob", color }]);
  currentData = matrix;
}

function fieldMap(obj, field) {
  return Object.fromEntries(
    Object.entries(obj || {}).map(([key, value]) => [key, value[field]])
  );
}

function histogram(values) {
  return values.reduce((hist, value) => {
    hist[value] = (hist[value] || 0) + 1;
    return hist;
  }, {});
}

function renderChartForResponse(data) {
  if (data.distribution && data.distribution.probabilities) {
    renderHistogram(data.distribution.probabilities, "v Probability");
    return;
  }

  if (data.high_v_frequency) {
    renderHistogram(fieldMap(data.high_v_frequency, "frequency"), "High-v Frequency");
    return;
  }

  if (data.one_step) {
    renderHistogram(fieldMap(data.one_step, "v"), "v by Residue");
    return;
  }

  if (data.probabilities) {
    renderHeatmap(data.probabilities);
    return;
  }

  if (data.times) {
    renderHistogram(histogram(data.times), "Time-to-v Count");
    return;
  }

  if (data.runs) {
    renderHistogram(histogram(data.runs), "Expansion Run Count");
    return;
  }

  if (data.trajectories) {
    renderMultiLineChart(data.trajectories);
    return;
  }

  if (data.log_path) {
    renderLineChart(data.log_path, "Log Path");
    return;
  }

  clearChart();
}

function summarizeTimes(data) {
  const times = data.times;

  if (!times || times.length === 0) {
    return {
      start: data.start,
      threshold: data.threshold,
      sampled_count: data.sampled_count,
      count: 0,
      message: "No threshold hits returned.",
    };
  }

  const sorted = [...times].sort((a, b) => a - b);
  const mean = times.reduce((a, b) => a + b, 0) / times.length;
  const median = sorted[Math.floor(sorted.length / 2)];
  const max = Math.max(...times);

  return {
    start: data.start,
    threshold: data.threshold,
    sampled_count: data.sampled_count,
    hits: times.length,
    mean,
    median,
    max,
    times,
  };
}

controls.trajectory.button.addEventListener("click", async () => {
  const params = {
    n: valueOf(controls.trajectory.n, "27"),
  };

  await runAnalysis(
    "Computing trajectory...",
    buildUrl("/api/trajectory", params)
  );
});

controls.vAnalysis.button.addEventListener("click", async () => {
  const params = {
    start: valueOf(controls.vAnalysis.start, "1"),
    count: valueOf(controls.vAnalysis.count, "10000"),
    max_v: valueOf(controls.vAnalysis.maxV, "10"),
    lag1: valueOf(controls.vAnalysis.lag1, "1"),
    lag2: valueOf(controls.vAnalysis.lag2, "2"),
  };

  await runAnalysis(
    "Running v analysis...",
    buildUrl("/api/v-analysis", params)
  );
});

controls.residue.button.addEventListener("click", async () => {
  const params = {
    start: valueOf(controls.residue.start, "1"),
    mod: valueOf(controls.residue.mod, "16"),
    count: valueOf(controls.residue.count, "20000"),
    threshold: valueOf(controls.residue.threshold, "3"),
  };

  await runAnalysis(
    "Running residue analysis...",
    buildUrl("/api/residue-analysis", params)
  );
});

controls.transitions.button.addEventListener("click", async () => {
  const params = {
    mod: valueOf(controls.transitions.mod, "16"),
    steps: valueOf(controls.transitions.steps, "5"),
  };

  await runAnalysis(
    "Computing residue transitions...",
    buildUrl("/api/transitions", params)
  );
});

controls.timeToV.button.addEventListener("click", async () => {
  const params = {
    start: valueOf(controls.timeToV.start, "1"),
    threshold: valueOf(controls.timeToV.threshold, "3"),
    count: valueOf(controls.timeToV.count, "5000"),
  };

  await runAnalysis(
    "Running time-to-v analysis...",
    buildUrl("/api/time-to-v", params),
    summarizeTimes
  );
});

controls.driftTrajectories.button.addEventListener("click", async () => {
  const params = {
    start: valueOf(controls.driftTrajectories.start, "1"),
    count: valueOf(controls.driftTrajectories.count, "100"),
    max_steps: valueOf(controls.driftTrajectories.maxSteps, "200"),
  };

  await runAnalysis(
    "Computing cumulative drift trajectories...",
    buildUrl("/api/drift-trajectories", params)
  );
});

controls.expansionRuns.button.addEventListener("click", async () => {
  const params = {
    start: valueOf(controls.expansionRuns.start, "1"),
    count: valueOf(controls.expansionRuns.count, "5000"),
    max_steps: valueOf(controls.expansionRuns.maxSteps, "200"),
  };

  await runAnalysis(
    "Running expansion run analysis...",
    buildUrl("/api/expansion-runs", params)
  );
});

controls.vTransitions.button.addEventListener("click", async () => {
  const params = {
    start: valueOf(controls.vTransitions.start, "1"),
    count: valueOf(controls.vTransitions.count, "5000"),
    max_steps: valueOf(controls.vTransitions.maxSteps, "100"),
    max_v: valueOf(controls.vTransitions.maxV, "10"),
  };

  await runAnalysis(
    "Computing v transition matrix...",
    buildUrl("/api/v-transitions", params)
  );
});

async function copyText(text) {
  await navigator.clipboard.writeText(text);
}

copyJsonButton.addEventListener("click", async () => {
  await copyText(output.textContent);
});

copyDataButton.addEventListener("click", async () => {
  await copyText(JSON.stringify(currentData, null, 2));
});

copyImageButton.addEventListener("click", async () => {
  chartCanvas.toBlob(async (blob) => {
    if (!blob) {
      return;
    }

    if (window.ClipboardItem) {
      const item = new ClipboardItem({ "image/png": blob });
      await navigator.clipboard.write([item]);
      return;
    }

    await copyText(chartCanvas.toDataURL("image/png"));
  });
});
