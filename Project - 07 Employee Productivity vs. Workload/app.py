"""
Flask Web Application for Project - 07: Employee Productivity vs. Workload
Microsoft Corporation - Workforce Intelligence & Autonomous Operations System

Serves:
- Executive Obsidian Dark Glassmorphic Web Dashboard
- REST API endpoints for telemetry, Overwork Paradox diagnostics, and ML feature attribution
- Real-time Interactive What-If Workload Policy Simulator
- Direct Publication-Grade PDF Report Delivery
"""

import os
import sys
import json
import pandas as pd
from flask import Flask, render_template, jsonify, request, send_file

# Add project root to path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from data.data_generator import generate_telemetry_dataset
from models.productivity_analyzer import ProductivityAnalyzer
from models.intervention_engine import InterventionEngine
from models.workload_simulator import WorkloadSimulator
from report.generate_pdf_report import build_pdf_report

app = Flask(__name__, static_folder="static", template_folder="templates")

# File paths
DATA_DIR = os.path.join(base_dir, "data")
CSV_PATH = os.path.join(DATA_DIR, "microsoft_workforce_productivity.csv")
REPORT_PATH = os.path.join(base_dir, "report", "Microsoft_Productivity_vs_Workload_Report.pdf")

# Ingest or generate data if not present
if not os.path.exists(CSV_PATH):
    print("Generating Microsoft workforce productivity telemetry dataset...")
    generate_telemetry_dataset(num_records=12500, output_dir=DATA_DIR)

print("Initializing Productivity Analyzer & Training Machine Learning Models...")
analyzer = ProductivityAnalyzer(CSV_PATH)
ml_metrics = analyzer.train_ml_models()
engine = InterventionEngine(analyzer.df)
simulator = WorkloadSimulator(analyzer.df, reg_model=analyzer.reg_model, feature_names=analyzer.feature_names)

# Ensure PDF report exists
if not os.path.exists(REPORT_PATH):
    print("Compiling publication-grade executive PDF report...")
    build_pdf_report(analyzer, engine, simulator, REPORT_PATH)

# =====================================================================
# ROUTES & REST ENDPOINTS
# =====================================================================

@app.route("/")
def index():
    """Renders the Obsidian Dark glassmorphic dashboard."""
    return render_template("index.html")

@app.route("/api/health")
def health():
    """System health check."""
    return jsonify({
        "status": "healthy",
        "service": "Microsoft Workforce Telemetry AI Diagnostics",
        "version": "1.0.0",
        "headcount_monitored": len(analyzer.df)
    })

@app.route("/api/kpis")
def get_kpis():
    """Returns top executive scorecard metrics."""
    kpis = analyzer.get_enterprise_kpis()
    return jsonify(kpis)

@app.route("/api/paradox_curve")
def get_paradox_curve():
    """Returns curve points and polynomial fit for The Overwork Paradox."""
    curve = analyzer.analyze_overwork_paradox_curve()
    return jsonify(curve)

@app.route("/api/bottlenecks")
def get_bottlenecks():
    """Returns divisional and bottleneck diagnostic distributions."""
    diag = analyzer.get_divisional_diagnostics()
    return jsonify(diag)

@app.route("/api/feature_importance")
def get_feature_importance():
    """Returns top AI feature attribution weights."""
    return jsonify(ml_metrics.get("top_features", []))

@app.route("/api/fatigue_aggregates")
def get_fatigue_aggregates():
    """Returns fatigue tiers cross-tabulated with sick days and Glint scores."""
    bins = [0, 25, 45, 65, 85, 100]
    labels = ["Low (<25)", "Moderate (25-45)", "Elevated (45-65)", "Severe (65-85)", "Critical (85+)"]
    temp = analyzer.df.copy()
    temp["tier"] = pd.cut(temp["cognitive_fatigue_index"], bins=bins, labels=labels, right=True)
    agg = temp.groupby("tier", observed=False).agg({
        "unplanned_sick_days": "mean",
        "glint_work_life_balance": "mean"
    }).reset_index().round(2)
    return jsonify(agg.to_dict(orient="records"))

@app.route("/api/simulate", methods=["POST"])
def simulate_policy():
    """
    Executes what-if workload policy simulation.
    Expects JSON: {
        meeting_reduction_pct: float,
        max_overtime_cap_hours: float,
        focus_time_shield_days: float,
        backlog_rebalance_factor: float
    }
    """
    data = request.get_json() or {}
    meeting_red = float(data.get("meeting_reduction_pct", 25.0))
    ot_cap = float(data.get("max_overtime_cap_hours", 45.0))
    focus_days = float(data.get("focus_time_shield_days", 1.5))
    rebal_fac = float(data.get("backlog_rebalance_factor", 20.0))
    
    sim_result = simulator.run_simulation(
        meeting_reduction_pct=meeting_red,
        max_overtime_cap_hours=ot_cap,
        focus_time_shield_days=focus_days,
        backlog_rebalance_factor=rebal_fac
    )
    return jsonify(sim_result)

@app.route("/api/telemetry")
def get_telemetry():
    """Returns raw employee telemetry records for data exploration."""
    limit = int(request.args.get("limit", 500))
    df_sample = analyzer.df.head(limit)
    return jsonify(df_sample.to_dict(orient="records"))

@app.route("/api/playbook")
def get_playbook():
    """Returns structured prescriptive intervention protocols."""
    pb = engine.get_prescriptive_playbook()
    return jsonify(pb)

@app.route("/api/roi")
def get_macro_roi():
    """Returns enterprise financial ROI breakdown."""
    roi = engine.compute_enterprise_intervention_roi()
    return jsonify(roi)

@app.route("/api/download_report")
def download_pdf_report():
    """Directly serves the publication-grade executive PDF report."""
    if not os.path.exists(REPORT_PATH):
        build_pdf_report(analyzer, engine, simulator, REPORT_PATH)
    return send_file(
        REPORT_PATH,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="Microsoft_Productivity_vs_Workload_Report.pdf"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5007))
    print(f"\n==========================================================================")
    print(f" MICROSOFT WORKFORCE PRODUCTIVITY AI SYSTEM ACTIVE")
    print(f" Dashboard URL: http://localhost:{port}")
    print(f" Executive PDF Report: http://localhost:{port}/api/download_report")
    print(f"==========================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)

