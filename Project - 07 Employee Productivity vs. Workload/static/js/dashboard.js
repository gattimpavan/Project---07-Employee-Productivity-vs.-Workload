/**
 * Microsoft Workforce Intelligence Dashboard Controller
 * Project - 07: Employee Productivity vs. Workload
 */

let charts = {};
let allTelemetry = [];
let currentPage = 1;
const PAGE_SIZE = 12;

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadDashboardKPIs();
    loadOverworkParadoxChart();
    loadBottleneckChart();
    loadFeatureImportanceChart();
    loadFatigueAbsenteeismChart();
    initSimulator();
    initTelemetryExplorer();
    loadPlaybook();
});

// -------------------------------------------------------------
// Tabs System
// -------------------------------------------------------------
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-tab");
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
            
            btn.classList.add("active");
            const targetEl = document.getElementById(targetId);
            if (targetEl) targetEl.classList.add("active");
            
            // Trigger chart resize if needed
            Object.values(charts).forEach(c => c && c.resize && c.resize());
        });
    });
}

// -------------------------------------------------------------
// Load High-Level KPIs
// -------------------------------------------------------------
async function loadDashboardKPIs() {
    try {
        const res = await fetch("/api/kpis");
        const data = await res.json();
        
        document.getElementById("kpi-headcount").innerText = data.total_headcount.toLocaleString();
        document.getElementById("kpi-hours").innerText = data.avg_weekly_hours;
        document.getElementById("kpi-ot-pct").innerText = data.chronic_overtime_rate_pct + "%";
        document.getElementById("kpi-meetings").innerText = data.avg_weekly_meeting_hours;
        document.getElementById("kpi-focus").innerText = data.avg_focus_time_hours;
        document.getElementById("kpi-completion").innerText = data.avg_task_completion_rate_pct + "%";
        document.getElementById("kpi-bugs").innerText = data.avg_bug_reopen_rate_pct + "%";
        document.getElementById("kpi-epi").innerText = data.avg_effective_productivity_index;
        document.getElementById("kpi-loss").innerText = "$" + data.total_productivity_loss_millions + "M";
        
        // Render Bottlenecks Grid
        renderBottlenecksGrid(data.bottleneck_breakdown);
    } catch (err) {
        console.error("Failed to load KPIs:", err);
    }
}

// -------------------------------------------------------------
// Chart 1: The Overwork Paradox Curve
// -------------------------------------------------------------
async function loadOverworkParadoxChart() {
    try {
        const res = await fetch("/api/paradox_curve");
        const payload = await res.json();
        const curveData = payload.curve_data;
        
        const labels = curveData.map(d => d.hours_bucket);
        const epiValues = curveData.map(d => d.effective_productivity_index);
        const bugValues = curveData.map(d => d.bug_reopen_rate);
        const completionValues = curveData.map(d => (d.task_completion_rate * 100).toFixed(1));
        
        const ctx = document.getElementById("chartParadox").getContext("2d");
        if (charts.paradox) charts.paradox.destroy();
        
        charts.paradox = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Effective Productivity Index (0-100)",
                        data: epiValues,
                        borderColor: "#0078d4",
                        backgroundColor: "rgba(0, 120, 212, 0.15)",
                        borderWidth: 3,
                        tension: 0.35,
                        fill: true,
                        yAxisID: "y"
                    },
                    {
                        label: "Sprint Task Completion Rate (%)",
                        data: completionValues,
                        borderColor: "#107c41",
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.2,
                        yAxisID: "y"
                    },
                    {
                        label: "Bug Reopen Rate (%)",
                        data: bugValues,
                        borderColor: "#d83b01",
                        backgroundColor: "rgba(216, 59, 1, 0.1)",
                        borderWidth: 2.5,
                        tension: 0.3,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: "#cbd5e1", font: { size: 11, family: "Segoe UI" } }
                    },
                    tooltip: {
                        backgroundColor: "rgba(15, 23, 42, 0.95)",
                        titleColor: "#38bdf8",
                        bodyColor: "#f8fafc",
                        borderColor: "rgba(255, 255, 255, 0.15)",
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#94a3b8", font: { size: 10 } }
                    },
                    y: {
                        type: "linear",
                        position: "left",
                        min: 0,
                        max: 100,
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#00bcf2", font: { size: 10 } },
                        title: { display: true, text: "Productivity / Completion (%)", color: "#00bcf2", font: { size: 11 } }
                    },
                    y1: {
                        type: "linear",
                        position: "right",
                        min: 0,
                        max: 50,
                        grid: { drawOnChartArea: false },
                        ticks: { color: "#f87171", font: { size: 10 } },
                        title: { display: true, text: "Bug Reopen Rate (%)", color: "#f87171", font: { size: 11 } }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Failed to load Paradox curve:", err);
    }
}

// -------------------------------------------------------------
// Chart 2: Divisional Bottlenecks Breakdown
// -------------------------------------------------------------
async function loadBottleneckChart() {
    try {
        const res = await fetch("/api/bottlenecks");
        const data = await res.json();
        const divBottlenecks = data.bottlenecks_by_division;
        
        const divisions = divBottlenecks.map(d => d.division.replace(" & ", " &\n"));
        const keys = Object.keys(divBottlenecks[0]).filter(k => k !== "division");
        const colorsPalette = ["#f59e0b", "#ef4444", "#dc2626", "#0078d4", "#107c41", "#8b5cf6"];
        
        const datasets = keys.map((key, idx) => ({
            label: key,
            data: divBottlenecks.map(d => d[key]),
            backgroundColor: colorsPalette[idx % colorsPalette.length]
        }));
        
        const ctx = document.getElementById("chartBottlenecks").getContext("2d");
        if (charts.bottlenecks) charts.bottlenecks.destroy();
        
        charts.bottlenecks = new Chart(ctx, {
            type: "bar",
            data: {
                labels: divisions,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#cbd5e1", font: { size: 9.5 }, boxWidth: 12 }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        max: 100,
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#94a3b8", callback: v => v + "%" }
                    },
                    y: {
                        stacked: true,
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#cbd5e1", font: { size: 10 } }
                    }
                }
            }
        });
        
        renderDivisionalTable(data.divisions);
    } catch (err) {
        console.error("Failed to load bottleneck chart:", err);
    }
}

// -------------------------------------------------------------
// Chart 3: AI Feature Importance
// -------------------------------------------------------------
async function loadFeatureImportanceChart() {
    try {
        const res = await fetch("/api/feature_importance");
        const features = await res.json();
        
        const labels = features.map(f => f.display_name).slice(0, 8);
        const prodData = features.map(f => (f.productivity_importance * 100).toFixed(1)).slice(0, 8);
        const botData = features.map(f => (f.bottleneck_importance * 100).toFixed(1)).slice(0, 8);
        
        const ctx = document.getElementById("chartFeatures").getContext("2d");
        if (charts.features) charts.features.destroy();
        
        charts.features = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Productivity Decay Driver (%)",
                        data: prodData,
                        backgroundColor: "#0078d4"
                    },
                    {
                        label: "Bottleneck Classification Driver (%)",
                        data: botData,
                        backgroundColor: "#00bcf2"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        labels: { color: "#cbd5e1", font: { size: 10 } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#94a3b8" }
                    },
                    y: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#cbd5e1", font: { size: 9.5 } }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Failed to load feature importance:", err);
    }
}

// -------------------------------------------------------------
// Chart 4: Cognitive Fatigue vs Absenteeism & Glint
// -------------------------------------------------------------
async function loadFatigueAbsenteeismChart() {
    try {
        const res = await fetch("/api/fatigue_aggregates");
        const data = await res.json();
        
        const labels = data.map(d => d.tier);
        const sickDays = data.map(d => d.unplanned_sick_days);
        const glintWLB = data.map(d => d.glint_work_life_balance);
        
        const ctx = document.getElementById("chartFatigue").getContext("2d");
        if (charts.fatigue) charts.fatigue.destroy();
        
        charts.fatigue = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        type: "bar",
                        label: "Avg Unplanned Sick Days / Qtr",
                        data: sickDays,
                        backgroundColor: "rgba(220, 38, 38, 0.7)",
                        borderColor: "#dc2626",
                        borderWidth: 1,
                        yAxisID: "y"
                    },
                    {
                        type: "line",
                        label: "Microsoft Glint WLB Score (1-5)",
                        data: glintWLB,
                        borderColor: "#107c41",
                        backgroundColor: "rgba(16, 124, 65, 0.2)",
                        borderWidth: 3,
                        pointRadius: 5,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: "#cbd5e1", font: { size: 10 } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#cbd5e1", font: { size: 9.5 } }
                    },
                    y: {
                        type: "linear",
                        position: "left",
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#f87171" },
                        title: { display: true, text: "Sick Days / Qtr", color: "#f87171" }
                    },
                    y1: {
                        type: "linear",
                        position: "right",
                        min: 1.0,
                        max: 5.0,
                        grid: { drawOnChartArea: false },
                        ticks: { color: "#4ade80" },
                        title: { display: true, text: "Glint WLB Score", color: "#4ade80" }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Failed to load fatigue chart:", err);
    }
}

// -------------------------------------------------------------
// Bottlenecks Grid Renderer
// -------------------------------------------------------------
function renderBottlenecksGrid(breakdown) {
    const container = document.getElementById("bottlenecks-grid");
    if (!container) return;
    
    const descriptions = {
        "Meeting & Collaboration Fragmentation": {
            desc: "Severe calendar fragmentation (>18 hrs meetings/week, focus time <8 hrs). Continuous context switching stalls deep engineering flow.",
            remedy: "Enforce 'No-Meeting Wednesdays' & default 25/50 min meetings.",
            cls: "frag"
        },
        "Chronic Overtime & Cognitive Exhaustion": {
            desc: "Engineers logging >50 hrs/wk and high weekend hours. Cognitive fatigue index >68 leads to exponential error rates and sleep deficit.",
            remedy: "Cap weekly hours at 45.0 hrs; enforce 48-hr post-incident rest.",
            cls: "ot"
        },
        "Rework Loops & Technical Debt Quagmire": {
            desc: "High bug reopening rate (>22%) and severe code churn (>32%). Developers spend majority of sprint fixing regressions instead of shipping value.",
            remedy: "Ring-fence 20% sprint quota for technical debt & test automation.",
            cls: "rework"
        },
        "Capacity Instability & Absenteeism Cascade": {
            desc: "Unplanned sick leaves (>6 days/qtr) and burnout episodes destabilize sprint handoffs and overburden remaining teammates.",
            remedy: "Trigger Viva manager support tripwires and flexible rest sabbaticals.",
            cls: "absent"
        },
        "Asymmetric Workload Overburden": {
            desc: "Story points (>44) and active tickets disproportionately concentrated on senior engineers with insufficient junior delegation.",
            remedy: "Enforce max WIP limit of 2 items; pair senior & junior SDEs.",
            cls: "overload"
        },
        "Optimal / Balanced Throughput": {
            desc: "Sustainable 40-42 hour work weeks, healthy focus blocks, low bug reopen rates, and high Microsoft Glint satisfaction.",
            remedy: "Protect healthy practices; benchmark team practices across org.",
            cls: "optimal"
        }
    };
    
    container.innerHTML = "";
    for (const [name, count] of Object.entries(breakdown)) {
        const meta = descriptions[name] || { desc: "Operational bottleneck.", remedy: "Intervene.", cls: "frag" };
        const card = document.createElement("div");
        card.className = `glass-panel bn-card ${meta.cls}`;
        card.innerHTML = `
            <div class="bn-head">
                <h4>${name}</h4>
                <span class="bn-count-badge">${count.toLocaleString()} (${((count/12500)*100).toFixed(1)}%)</span>
            </div>
            <p class="bn-desc">${meta.desc}</p>
            <div class="bn-remedy">
                <div class="bn-remedy-title">Mandated Intervention</div>
                <div class="bn-remedy-text">${meta.remedy}</div>
            </div>
        `;
        container.appendChild(card);
    }
}

// -------------------------------------------------------------
// Divisional Breakdown Table
// -------------------------------------------------------------
function renderDivisionalTable(divisions) {
    const tbody = document.getElementById("divisional-table-body");
    if (!tbody) return;
    tbody.innerHTML = "";
    
    divisions.forEach(d => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${d.division}</strong></td>
            <td>${d.headcount.toLocaleString()}</td>
            <td>${d.weekly_hours} hrs</td>
            <td>${d.weekly_meeting_hours} hrs</td>
            <td>${d.focus_time_hours} hrs</td>
            <td>${d.task_completion_pct}%</td>
            <td>${d.effective_productivity_index}</td>
            <td style="color: #f87171; font-weight: bold;">$${d.loss_millions}M</td>
        `;
        tbody.appendChild(tr);
    });
}

// -------------------------------------------------------------
// What-If Workload Policy Simulator
// -------------------------------------------------------------
function initSimulator() {
    const sMeeting = document.getElementById("sim-meeting");
    const sOvertime = document.getElementById("sim-overtime");
    const sFocus = document.getElementById("sim-focus");
    const sRebalance = document.getElementById("sim-rebalance");
    
    const vMeeting = document.getElementById("val-sim-meeting");
    const vOvertime = document.getElementById("val-sim-overtime");
    const vFocus = document.getElementById("val-sim-focus");
    const vRebalance = document.getElementById("val-sim-rebalance");
    
    function updateSimulator() {
        vMeeting.innerText = sMeeting.value + "%";
        vOvertime.innerText = sOvertime.value + " hrs";
        vFocus.innerText = sFocus.value + " days";
        vRebalance.innerText = sRebalance.value + "%";
        
        triggerSimulation({
            meeting_reduction_pct: parseFloat(sMeeting.value),
            max_overtime_cap_hours: parseFloat(sOvertime.value),
            focus_time_shield_days: parseFloat(sFocus.value),
            backlog_rebalance_factor: parseFloat(sRebalance.value)
        });
    }
    
    [sMeeting, sOvertime, sFocus, sRebalance].forEach(sl => {
        sl.addEventListener("input", updateSimulator);
    });
    
    // Initial trigger
    updateSimulator();
}

let simTimeout = null;
async function triggerSimulation(payload) {
    clearTimeout(simTimeout);
    simTimeout = setTimeout(async () => {
        try {
            const res = await fetch("/api/simulate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            // Update Metric Outputs
            document.getElementById("sim-out-lift").innerText = "+" + data.delta.productivity_lift_pct + " pts";
            document.getElementById("sim-out-completion").innerText = "+" + data.delta.task_completion_improvement_pct + "%";
            document.getElementById("sim-out-meetings").innerText = "-" + data.delta.meeting_hours_reclaimed_weekly + " hrs/wk";
            document.getElementById("sim-out-focus").innerText = "+" + data.delta.focus_hours_gained_weekly + " hrs/wk";
            document.getElementById("sim-out-bugs").innerText = "-" + data.delta.bug_reopen_reduction_pct + "%";
            document.getElementById("sim-out-savings").innerText = "$" + data.delta.net_financial_savings_millions + "M";
            
            // Render / Update Simulator Chart
            renderSimulatorChart(data.baseline, data.simulated);
        } catch (err) {
            console.error("Simulation error:", err);
        }
    }, 150);
}

function renderSimulatorChart(b, s) {
    const ctx = document.getElementById("chartSimulation").getContext("2d");
    const labels = ["Weekly Hours", "Meeting Hours", "Focus Blocks", "Task Compl. %", "Bug Reopen %", "EPI Index"];
    
    const bVals = [b.avg_weekly_hours, b.avg_meeting_hours, b.avg_focus_time, b.avg_task_completion_pct, b.avg_bug_reopen_rate, b.avg_effective_productivity_index];
    const sVals = [s.avg_weekly_hours, s.avg_meeting_hours, s.avg_focus_time, s.avg_task_completion_pct, s.avg_bug_reopen_rate, s.avg_effective_productivity_index];
    
    if (charts.sim) {
        charts.sim.data.datasets[0].data = bVals;
        charts.sim.data.datasets[1].data = sVals;
        charts.sim.update();
        return;
    }
    
    charts.sim = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Baseline (Status Quo)",
                    data: bVals,
                    backgroundColor: "rgba(148, 163, 184, 0.7)"
                },
                {
                    label: "Simulated (With Interventions)",
                    data: sVals,
                    backgroundColor: "#0078d4"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: "#cbd5e1" } }
            },
            scales: {
                x: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#cbd5e1", font: { size: 10 } }
                },
                y: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#94a3b8" }
                }
            }
        }
    });
}

// -------------------------------------------------------------
// Telemetry Explorer
// -------------------------------------------------------------
async function initTelemetryExplorer() {
    try {
        const res = await fetch("/api/telemetry?limit=500");
        allTelemetry = await res.json();
        
        // Populate Filter Dropdowns
        const divisions = [...new Set(allTelemetry.map(t => t.division))];
        const roles = [...new Set(allTelemetry.map(t => t.role))];
        const bottlenecks = [...new Set(allTelemetry.map(t => t.primary_bottleneck))];
        
        populateSelect("filter-div", divisions);
        populateSelect("filter-role", roles);
        populateSelect("filter-bn", bottlenecks);
        
        // Search & Filters Listener
        document.getElementById("search-emp").addEventListener("input", () => { currentPage = 1; renderTelemetryTable(); });
        document.getElementById("filter-div").addEventListener("change", () => { currentPage = 1; renderTelemetryTable(); });
        document.getElementById("filter-role").addEventListener("change", () => { currentPage = 1; renderTelemetryTable(); });
        document.getElementById("filter-bn").addEventListener("change", () => { currentPage = 1; renderTelemetryTable(); });
        
        document.getElementById("btn-prev").addEventListener("click", () => {
            if (currentPage > 1) { currentPage--; renderTelemetryTable(); }
        });
        document.getElementById("btn-next").addEventListener("click", () => {
            currentPage++;
            renderTelemetryTable();
        });
        
        renderTelemetryTable();
    } catch (err) {
        console.error("Failed to load telemetry:", err);
    }
}

function populateSelect(id, options) {
    const sel = document.getElementById(id);
    if (!sel) return;
    options.forEach(opt => {
        const o = document.createElement("option");
        o.value = opt;
        o.innerText = opt;
        sel.appendChild(o);
    });
}

function renderTelemetryTable() {
    const searchVal = document.getElementById("search-emp").value.toLowerCase();
    const divVal = document.getElementById("filter-div").value;
    const roleVal = document.getElementById("filter-role").value;
    const bnVal = document.getElementById("filter-bn").value;
    
    const filtered = allTelemetry.filter(row => {
        const matchSearch = !searchVal || row.employee_id.toLowerCase().includes(searchVal) || row.role.toLowerCase().includes(searchVal);
        const matchDiv = !divVal || row.division === divVal;
        const matchRole = !roleVal || row.role === roleVal;
        const matchBn = !bnVal || row.primary_bottleneck === bnVal;
        return matchSearch && matchDiv && matchRole && matchBn;
    });
    
    const totalPages = Math.ceil(filtered.length / PAGE_SIZE) || 1;
    if (currentPage > totalPages) currentPage = totalPages;
    
    document.getElementById("page-info").innerText = `Page ${currentPage} of ${totalPages} (${filtered.length} engineers)`;
    document.getElementById("btn-prev").disabled = currentPage === 1;
    document.getElementById("btn-next").disabled = currentPage === totalPages;
    
    const startIdx = (currentPage - 1) * PAGE_SIZE;
    const pageRows = filtered.slice(startIdx, startIdx + PAGE_SIZE);
    
    const tbody = document.getElementById("telemetry-tbody");
    tbody.innerHTML = "";
    
    pageRows.forEach(r => {
        const tr = document.createElement("tr");
        
        let bnClass = "badge-frag";
        if (r.primary_bottleneck.includes("Overtime")) bnClass = "badge-ot";
        else if (r.primary_bottleneck.includes("Rework")) bnClass = "badge-rework";
        else if (r.primary_bottleneck.includes("Absenteeism")) bnClass = "badge-absent";
        else if (r.primary_bottleneck.includes("Optimal")) bnClass = "badge-optimal";
        
        tr.innerHTML = `
            <td><strong>${r.employee_id}</strong></td>
            <td>${r.division}</td>
            <td>${r.role}</td>
            <td>${r.weekly_hours}h</td>
            <td>${r.weekly_meeting_hours}h</td>
            <td>${r.focus_time_hours}h</td>
            <td>${(r.task_completion_rate * 100).toFixed(0)}%</td>
            <td>${r.bug_reopen_rate}%</td>
            <td>${r.glint_work_life_balance}</td>
            <td><strong>${r.effective_productivity_index}</strong></td>
            <td><span class="badge-bottleneck ${bnClass}">${r.primary_bottleneck}</span></td>
            <td style="font-size: 0.70rem; color: #cbd5e1;">${r.intervention_recommendation}</td>
        `;
        tbody.appendChild(tr);
    });
}

// -------------------------------------------------------------
// Playbook Loader
// -------------------------------------------------------------
async function loadPlaybook() {
    try {
        const res = await fetch("/api/playbook");
        const pb = await res.json();
        
        renderPlaybookCards("playbook-h1", pb.immediate_0_30_days);
        renderPlaybookCards("playbook-h2", pb.operational_30_90_days);
        renderPlaybookCards("playbook-h3", pb.systemic_90_plus_days);
    } catch (err) {
        console.error("Failed to load playbook:", err);
    }
}

function renderPlaybookCards(containerId, list) {
    const c = document.getElementById(containerId);
    if (!c) return;
    c.innerHTML = "";
    
    list.forEach(p => {
        const card = document.createElement("div");
        card.className = "glass-panel p-card";
        card.innerHTML = `
            <div class="p-card-header">
                <span class="p-card-id">${p.protocol_id}</span>
                <span class="p-card-pillar">${p.pillar}</span>
            </div>
            <div class="p-card-title">${p.title}</div>
            <div class="p-card-body">${p.action}</div>
            <div style="font-size: 0.72rem; color: #4ade80; margin-bottom: 8px;">
                <strong>Impact:</strong> ${p.expected_impact}
            </div>
            <div class="p-card-footer">
                <span class="p-target">${p.target_metric}</span>
                <span class="p-owner">Owner: ${p.owner}</span>
            </div>
        `;
        c.appendChild(card);
    });
}

