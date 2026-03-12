/* global bootstrap, Chart */

const API_BASE = "/api/analytics";

function showErrorToast(message) {
  const toastEl = document.getElementById("errorToast");
  const bodyEl = document.getElementById("errorToastBody");
  if (!toastEl || !bodyEl) return;
  bodyEl.textContent = message || "Failed to load data from API.";
  const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
  toast.show();
}

async function fetchJson(path) {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}

function updateSummaryCards(dashboard) {
  const hostsCountEl = document.getElementById("hosts-count");
  const reportsCountEl = document.getElementById("reports-count");
  const failsCountEl = document.getElementById("fails-count");
  const indexEl = document.getElementById("security-index");
  const barEl = document.getElementById("security-bar");
  const levelLabelEl = document.getElementById("security-level-label");

  if (!dashboard) return;

  hostsCountEl.textContent = dashboard.hosts ?? "0";
  reportsCountEl.textContent = dashboard.reports ?? "0";
  failsCountEl.textContent = (dashboard.fails ?? 0) + (dashboard.errors ?? 0);

  const score = dashboard.security_index ?? 0;
  indexEl.textContent = `${score}%`;
  barEl.style.width = `${Math.min(score, 100)}%`;

  let level = "Unknown";
  let badgeClass = "bg-opacity-label";
  if (score >= 85) {
    level = "Excellent";
    badgeClass += " text-success";
  } else if (score >= 60) {
    level = "Good";
    badgeClass += " text-info";
  } else if (score >= 40) {
    level = "Elevated risk";
    badgeClass += " text-warning";
  } else {
    level = "Critical";
    badgeClass += " text-danger";
  }
  levelLabelEl.textContent = level;
  levelLabelEl.className = `badge rounded-pill ${badgeClass}`;
}

function renderTopRisksChart(topRisks) {
  const canvas = document.getElementById("topRisksChart");
  const emptyLabel = document.getElementById("top-risks-empty");
  if (!canvas) return;

  if (!Array.isArray(topRisks) || topRisks.length === 0) {
    emptyLabel.style.display = "block";
    return;
  }

  const labels = topRisks.map((r) => r.check_id);
  const counts = topRisks.map((r) => r.count);

  // eslint-disable-next-line no-new
  new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Failed checks",
          data: counts,
          backgroundColor: "rgba(77, 163, 255, 0.6)",
          borderRadius: 8
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          ticks: { color: "#8aa0c8" },
          grid: { display: false }
        },
        y: {
          ticks: { color: "#8aa0c8", precision: 0 },
          grid: { color: "rgba(255,255,255,0.05)" }
        }
      }
    }
  });
}

function renderStatusPieChart(dashboard) {
  const canvas = document.getElementById("statusPieChart");
  const emptyLabel = document.getElementById("status-pie-empty");
  if (!canvas || !dashboard) return;

  const total = dashboard.checks_total ?? 0;
  const fails = dashboard.fails ?? 0;
  const errors = dashboard.errors ?? 0;
  const passes = Math.max(total - fails - errors, 0);

  if (total === 0) {
    emptyLabel.style.display = "block";
    return;
  }

  const data = [passes, fails, errors];
  const labels = ["Pass", "Fail", "Error"];

  // eslint-disable-next-line no-new
  new Chart(canvas.getContext("2d"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data,
          backgroundColor: [
            "rgba(13, 202, 240, 0.8)",
            "rgba(220, 53, 69, 0.85)",
            "rgba(255, 193, 7, 0.9)"
          ],
          borderWidth: 0
        }
      ]
    },
    options: {
      plugins: {
        legend: {
          labels: { color: "#8aa0c8" }
        }
      },
      cutout: "70%"
    }
  });
}

function formatDateTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

function capitalize(str) {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function renderLatestChecks(latest) {
  const tbody = document.getElementById("latest-checks-body");
  const counter = document.getElementById("latest-checks-counter");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (!Array.isArray(latest) || latest.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center text-muted py-3">
          No checks yet. Run the agent on at least one host.
        </td>
      </tr>`;
    counter.textContent = "";
    return;
  }

  latest.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="fw-semibold">${item.title}</td>
      <td class="text-muted small">${item.hostname}</td>
      <td>
        <span class="badge-status ${item.status}">
          ${item.status.toUpperCase()}
        </span>
      </td>
      <td>
        <span class="severity-pill ${item.severity}">
          ${item.severity.toUpperCase()}
        </span>
      </td>
      <td class="text-end text-muted small">
        ${formatDateTime(item.timestamp)}
      </td>
    `;
    tbody.appendChild(tr);
  });

  counter.textContent = `${latest.length} checks`;
}

function renderHosts(hosts) {
  const tbody = document.getElementById("hosts-body");
  const counter = document.getElementById("hosts-counter");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (!Array.isArray(hosts) || hosts.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center text-muted py-3">
          No hosts yet. Install and run the agent.
        </td>
      </tr>`;
    counter.textContent = "";
    return;
  }

  hosts.forEach((h) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="fw-semibold">${h.hostname}</td>
      <td class="text-muted small">${h.ip || "-"}</td>
      <td class="text-muted small">${capitalize(h.os || "")}</td>
      <td class="text-end text-muted small">${formatDateTime(h.created_at)}</td>
    `;
    tbody.appendChild(tr);
  });

  counter.textContent = `${hosts.length} host${hosts.length > 1 ? "s" : ""}`;
}

async function initDashboard() {
  try {
    const [dashboard, topRisks, latestChecks, hosts] = await Promise.all([
      fetchJson(`${API_BASE}/dashboard`),
      fetchJson(`${API_BASE}/top-risks`),
      fetchJson(`${API_BASE}/latest-checks`),
      fetchJson(`${API_BASE}/hosts`)
    ]);

    updateSummaryCards(dashboard);
    renderTopRisksChart(topRisks);
    renderStatusPieChart(dashboard);
    renderLatestChecks(latestChecks);
    renderHosts(hosts);
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error(e);
    showErrorToast("Cannot load analytics data. Check that the API is running.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initDashboard();
});

