// Solaris FZ-500 Dashboard — frontend

const socket = io();
const CHART_WINDOW_SEC = 600;

// --------------------------------------------------------------------------
// Plotly chart
// --------------------------------------------------------------------------
const traceTcA = { x: [], y: [], mode: "lines", name: "TC-A (plate)", line: { color: "#ff7043", width: 2 } };
const traceTcB = { x: [], y: [], mode: "lines", name: "TC-B (plate)", line: { color: "#ffb300", width: 2 } };
const traceAir = { x: [], y: [], mode: "lines", name: "Air gap", line: { color: "#42a5f5", width: 2 } };

const chartLayout = {
  paper_bgcolor: "#151922",
  plot_bgcolor: "#0b0d12",
  font: { color: "#e6e9ef", family: "monospace" },
  margin: { t: 10, r: 20, b: 40, l: 50 },
  xaxis: { gridcolor: "#2a303d", zerolinecolor: "#2a303d", title: { text: "Time", font: { size: 11 } } },
  yaxis: { gridcolor: "#2a303d", zerolinecolor: "#2a303d", title: { text: "°C", font: { size: 11 } } },
  legend: { orientation: "h", y: -0.15, font: { size: 11 } },
  shapes: [],
};

Plotly.newPlot("chart", [traceTcA, traceTcB, traceAir], chartLayout, {
  responsive: true,
  displayModeBar: false,
});

// --------------------------------------------------------------------------
// Incoming data
// --------------------------------------------------------------------------
socket.on("history", (h) => {
  traceTcA.x = h.time.map((t) => new Date(t * 1000));
  traceTcA.y = h.tc_a;
  traceTcB.x = h.time.map((t) => new Date(t * 1000));
  traceTcB.y = h.tc_b;
  traceAir.x = h.time.map((t) => new Date(t * 1000));
  traceAir.y = h.air;
  Plotly.redraw("chart");
});

socket.on("reading", (r) => {
  const dt = new Date(r.t * 1000);
  Plotly.extendTraces(
    "chart",
    {
      x: [[dt], [dt], [dt]],
      y: [[r.tc_a], [r.tc_b], [r.air]],
    },
    [0, 1, 2],
    CHART_WINDOW_SEC
  );

  document.getElementById("r-tca").textContent = r.tc_a !== null && r.tc_a !== undefined ? r.tc_a.toFixed(1) : "--";
  document.getElementById("r-tcb").textContent = r.tc_b !== null && r.tc_b !== undefined ? r.tc_b.toFixed(1) : "--";
  document.getElementById("r-air").textContent = r.air !== null && r.air !== undefined ? r.air.toFixed(1) : "--";

  const lampInd = document.getElementById("lamp-ind");
  const lampState = document.getElementById("lamp-state");
  const lampTime = document.getElementById("lamp-time");
  if (r.lamp) {
    lampInd.classList.add("on");
    lampState.textContent = "ON";
    lampTime.textContent = `Elapsed: ${r.lamp_elapsed.toFixed(0)}s`;
  } else {
    lampInd.classList.remove("on");
    lampState.textContent = "OFF";
    lampTime.textContent = "—";
  }
});

socket.on("test_state", (s) => {
  const phaseEl = document.getElementById("test-phase");
  phaseEl.textContent = s.phase;
  phaseEl.className = "test-phase " + (s.phase || "idle");

  const startBtn = document.getElementById("test-start");
  const stopBtn = document.getElementById("test-stop");
  startBtn.disabled = s.active;
  stopBtn.disabled = !s.active;

  const meta = document.getElementById("test-meta");
  if (s.active) {
    const sampleLine = s.sample_id ? `<div><b>Sample:</b> ${s.sample_id}${s.test_name ? " · " + s.test_name : ""}</div>` : "";
    const fmt = (n) => {
      const m = Math.floor(n / 60).toString().padStart(2, "0");
      const sec = Math.floor(n % 60).toString().padStart(2, "0");
      return `${m}:${sec}`;
    };
    const phaseRem = s.phase_remaining_s !== undefined ? fmt(s.phase_remaining_s) : "--:--";
    const totalRem = s.total_remaining_s !== undefined ? fmt(s.total_remaining_s) : "--:--";
    meta.innerHTML = `
      <div style="margin-top:8px; font-size:28px; font-weight:600; font-variant-numeric:tabular-nums; color:var(--accent)">${phaseRem}</div>
      <div style="font-size:11px; color:var(--muted); letter-spacing:0.1em; text-transform:uppercase">remaining in phase</div>
      <div style="margin-top:8px; font-size:13px"><b>Elapsed:</b> ${fmt(s.elapsed_s)} &nbsp; <b>Total left:</b> ${totalRem}</div>
      ${sampleLine}
      <div style="font-size:11px; color:var(--muted); margin-top:4px">ID: ${s.id || ""}</div>
    `;
  } else if (s.id) {
    meta.innerHTML = `
      <div style="margin-top:6px"><b>Last test:</b> ${s.id}</div>
      <a href="/api/test/csv/${s.id}" style="color:#42a5f5;font-size:12px">Download CSV</a>
    `;
  } else {
    meta.innerHTML = "";
  }
});

// --------------------------------------------------------------------------
// Buttons
// --------------------------------------------------------------------------
let lampOn = false;
document.getElementById("lamp-toggle").addEventListener("click", async () => {
  lampOn = !lampOn;
  await fetch("/api/lamp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ on: lampOn }),
  });
  document.getElementById("lamp-toggle").textContent = lampOn ? "Manual OFF" : "Manual ON";
});

document.getElementById("test-start").addEventListener("click", async () => {
  const warmup = parseInt(document.getElementById("cfg-warmup").value);
  const lamp_on_sec = parseInt(document.getElementById("cfg-lamp").value);
  const cooldown = parseInt(document.getElementById("cfg-cool").value);
  const sample_id = document.getElementById("cfg-sample").value.trim();
  const test_name = document.getElementById("cfg-testname").value.trim();
  if (!sample_id) {
    alert("Sample ID is required — e.g. dryrun_01, bare_plate, NK-A3");
    document.getElementById("cfg-sample").focus();
    return;
  }
  const r = await fetch("/api/test/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      warmup_sec: warmup,
      lamp_on_sec,
      cooldown_sec: cooldown,
      sample_id,
      test_name,
    }),
  });
  if (!r.ok) {
    const err = await r.json();
    alert("Start failed: " + (err.error || r.status));
  }
});

document.getElementById("test-stop").addEventListener("click", async () => {
  if (!confirm("Stop the running test?")) return;
  await fetch("/api/test/stop", { method: "POST" });
});

// --------------------------------------------------------------------------
// Status + WiFi
// --------------------------------------------------------------------------
async function refreshStatus() {
  try {
    const s = await fetch("/api/state").then((r) => r.json());
    setDot("st-spi", s.spi_available, "SPI");
    setDot("st-ds", s.ds18b20_detected, "DS18B20");
    setDot("st-lamp", s.lamp_available, "Lamp");
  } catch (e) {}
  try {
    const w = await fetch("/api/wifi/status").then((r) => r.json());
    document.getElementById("st-wifi").innerHTML = `<span class="dot ok"></span>${w.ssid || "—"} · ${w.ip || "—"}`;
  } catch (e) {}
}

function setDot(elId, ok, label) {
  const el = document.getElementById(elId);
  el.innerHTML = `<span class="dot ${ok ? "ok" : "err"}"></span>${label}`;
}

async function refreshWifi() {
  try {
    const r = await fetch("/api/wifi/list").then((r) => r.json());
    const container = document.getElementById("wifi-list");
    container.innerHTML = "";
    (r.profiles || []).forEach((p) => {
      const btn = document.createElement("div");
      btn.className = "wifi-btn" + (p.active ? " active" : "");
      btn.innerHTML = `<span>${p.name}</span>${p.active ? '<span class="wifi-badge">active</span>' : ""}`;
      btn.addEventListener("click", async () => {
        if (p.active) return;
        if (!confirm(`Switch to "${p.name}"? The browser may briefly lose connection.`)) return;
        btn.innerHTML = `<span>${p.name}</span><span class="wifi-badge" style="background:#ffb300">switching…</span>`;
        try {
          await fetch("/api/wifi/switch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: p.name }),
          });
        } catch (e) {}
        setTimeout(refreshWifi, 3000);
        setTimeout(refreshStatus, 3000);
      });
      container.appendChild(btn);
    });
  } catch (e) {}
}

setInterval(() => {
  document.getElementById("footer-time").textContent = new Date().toLocaleTimeString();
}, 1000);

refreshStatus();
refreshWifi();
setInterval(refreshStatus, 5000);
setInterval(refreshWifi, 15000);
