"""
Productivity Analyzer & AI Diagnostic Engine
Project - 07: Employee Productivity vs. Workload
Microsoft Corporation - Engineering & Operations Telemetry Diagnostics
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder

class ProductivityAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = pd.read_csv(data_path)
        
        # ML Models
        self.reg_model = None
        self.clf_model = None
        self.feature_names = [
            "weekly_hours", "overtime_hours", "weekend_hours", "after_hours_teams_pings",
            "weekly_meeting_hours", "focus_time_hours", "context_switching_score",
            "active_ticket_count", "story_points_planned", "pr_cycle_time_hours",
            "bug_reopen_rate", "code_churn_rework_pct", "unplanned_sick_days",
            "glint_work_life_balance", "glint_manager_support", "glint_empowerment_autonomy",
            "cognitive_fatigue_index"
        ]
        self.label_encoder = LabelEncoder()
        self.model_metrics = {}
        
    def get_enterprise_kpis(self):
        """
        Computes high-level executive KPI scorecard for Microsoft leadership.
        """
        total_hc = len(self.df)
        avg_hours = round(float(self.df["weekly_hours"].mean()), 1)
        avg_ot = round(float(self.df["overtime_hours"].mean()), 1)
        chronic_ot_count = int((self.df["weekly_hours"] >= 48.0).sum())
        chronic_ot_pct = round(float(chronic_ot_count / total_hc * 100), 1)
        
        avg_meetings = round(float(self.df["weekly_meeting_hours"].mean()), 1)
        avg_focus = round(float(self.df["focus_time_hours"].mean()), 1)
        avg_epi = round(float(self.df["effective_productivity_index"].mean()), 1)
        avg_completion = round(float(self.df["task_completion_rate"].mean() * 100), 1)
        avg_spillover = round(float(self.df["sprint_spillover_rate"].mean() * 100), 1)
        avg_bug_reopen = round(float(self.df["bug_reopen_rate"].mean()), 1)
        avg_sick_days = round(float(self.df["unplanned_sick_days"].mean()), 1)
        avg_glint_wlb = round(float(self.df["glint_work_life_balance"].mean()), 2)
        total_loss_usd = round(float(self.df["productivity_loss_usd"].sum()), 2)
        total_loss_millions = round(total_loss_usd / 1e6, 1)
        
        bottleneck_counts = self.df["primary_bottleneck"].value_counts().to_dict()
        top_bottleneck = self.df["primary_bottleneck"].mode()[0]
        
        return {
            "total_headcount": total_hc,
            "avg_weekly_hours": avg_hours,
            "avg_overtime_hours": avg_ot,
            "chronic_overtime_rate_pct": chronic_ot_pct,
            "avg_weekly_meeting_hours": avg_meetings,
            "avg_focus_time_hours": avg_focus,
            "avg_effective_productivity_index": avg_epi,
            "avg_task_completion_rate_pct": avg_completion,
            "avg_sprint_spillover_rate_pct": avg_spillover,
            "avg_bug_reopen_rate_pct": avg_bug_reopen,
            "avg_unplanned_sick_days": avg_sick_days,
            "avg_glint_wlb": avg_glint_wlb,
            "total_productivity_loss_usd": total_loss_usd,
            "total_productivity_loss_millions": total_loss_millions,
            "bottleneck_breakdown": bottleneck_counts,
            "primary_bottleneck": top_bottleneck
        }

    def analyze_overwork_paradox_curve(self):
        """
        Quantifies the mathematical tipping point where increasing working hours
        yields diminishing and ultimately negative returns on effective output.
        """
        bins = [35, 40, 44, 48, 52, 56, 60, 65, 75]
        labels = ["36-40 hrs", "41-44 hrs", "45-48 hrs", "49-52 hrs", "53-56 hrs", "57-60 hrs", "61-65 hrs", "66+ hrs"]
        
        temp_df = self.df.copy()
        temp_df["hours_bucket"] = pd.cut(temp_df["weekly_hours"], bins=bins, labels=labels, right=True)
        
        curve = temp_df.groupby("hours_bucket", observed=False).agg({
            "weekly_hours": "mean",
            "effective_productivity_index": "mean",
            "story_points_completed": "mean",
            "task_completion_rate": "mean",
            "bug_reopen_rate": "mean",
            "cognitive_fatigue_index": "mean",
            "glint_work_life_balance": "mean",
            "unplanned_sick_days": "mean",
            "employee_id": "count"
        }).reset_index().rename(columns={"employee_id": "headcount"})
        
        curve = curve.round(2)
        
        # Fit quadratic curve: EPI = a*H^2 + b*H + c to locate peak H*
        valid_data = temp_df[["weekly_hours", "effective_productivity_index"]].dropna()
        poly_coeffs = np.polyfit(valid_data["weekly_hours"], valid_data["effective_productivity_index"], deg=2)
        # vertex of parabola: H* = -b / (2a)
        optimal_hours = round(float(-poly_coeffs[1] / (2 * poly_coeffs[0])), 1) if poly_coeffs[0] < 0 else 42.0
        
        return {
            "curve_data": curve.to_dict(orient="records"),
            "optimal_peak_hours": optimal_hours,
            "poly_coefficients": [round(float(c), 4) for c in poly_coeffs]
        }

    def train_ml_models(self):
        """
        Trains:
        1. Gradient Boosting Regressor for Effective Productivity Index (EPI).
        2. Random Forest Classifier for Primary Bottleneck classification.
        """
        X = self.df[self.feature_names].values
        y_reg = self.df["effective_productivity_index"].values
        y_clf = self.label_encoder.fit_transform(self.df["primary_bottleneck"])
        
        X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
            X, y_reg, y_clf, test_size=0.20, random_state=42
        )
        
        # Model 1: Gradient Boosting Regressor
        self.reg_model = GradientBoostingRegressor(
            n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42
        )
        self.reg_model.fit(X_train, y_reg_train)
        y_reg_pred = self.reg_model.predict(X_test)
        
        r2 = round(float(r2_score(y_reg_test, y_reg_pred)), 3)
        mae = round(float(mean_absolute_error(y_reg_test, y_reg_pred)), 2)
        
        # Model 2: Random Forest Classifier
        self.clf_model = RandomForestClassifier(
            n_estimators=100, max_depth=8, random_state=42
        )
        self.clf_model.fit(X_train, y_clf_train)
        y_clf_pred = self.clf_model.predict(X_test)
        
        acc = round(float(accuracy_score(y_clf_test, y_clf_pred)), 3)
        f1 = round(float(f1_score(y_clf_test, y_clf_pred, average="weighted")), 3)
        
        # Feature Importances
        clf_importances = self.clf_model.feature_importances_
        reg_importances = self.reg_model.feature_importances_
        
        feature_importance_list = []
        for name, reg_imp, clf_imp in zip(self.feature_names, reg_importances, clf_importances):
            feature_importance_list.append({
                "feature": name,
                "display_name": name.replace("_", " ").title(),
                "productivity_importance": round(float(reg_imp), 4),
                "bottleneck_importance": round(float(clf_imp), 4),
                "combined_importance": round(float((reg_imp + clf_imp) / 2.0), 4)
            })
            
        feature_importance_list = sorted(feature_importance_list, key=lambda x: x["combined_importance"], reverse=True)
        
        self.model_metrics = {
            "regression_r2": r2,
            "regression_mae": mae,
            "classifier_accuracy": acc,
            "classifier_f1": f1,
            "classes": list(self.label_encoder.classes_),
            "top_features": feature_importance_list[:10]
        }
        
        return self.model_metrics

    def get_divisional_diagnostics(self):
        """
        Computes detailed cross-divisional breakdown across Microsoft business units.
        """
        div_summary = self.df.groupby("division").agg({
            "employee_id": "count",
            "weekly_hours": "mean",
            "overtime_hours": "mean",
            "weekly_meeting_hours": "mean",
            "focus_time_hours": "mean",
            "context_switching_score": "mean",
            "task_completion_rate": "mean",
            "sprint_spillover_rate": "mean",
            "bug_reopen_rate": "mean",
            "cognitive_fatigue_index": "mean",
            "glint_work_life_balance": "mean",
            "unplanned_sick_days": "mean",
            "effective_productivity_index": "mean",
            "productivity_loss_usd": "sum"
        }).reset_index().rename(columns={"employee_id": "headcount"})
        
        div_summary["loss_millions"] = (div_summary["productivity_loss_usd"] / 1e6).round(1)
        div_summary["task_completion_pct"] = (div_summary["task_completion_rate"] * 100).round(1)
        div_summary["sprint_spillover_pct"] = (div_summary["sprint_spillover_rate"] * 100).round(1)
        
        # Round numerical columns
        for col in ["weekly_hours", "overtime_hours", "weekly_meeting_hours", "focus_time_hours",
                    "context_switching_score", "bug_reopen_rate", "cognitive_fatigue_index",
                    "glint_work_life_balance", "unplanned_sick_days", "effective_productivity_index"]:
            div_summary[col] = div_summary[col].round(2)
            
        # Divisional bottleneck distribution
        div_bottlenecks = pd.crosstab(
            self.df["division"], self.df["primary_bottleneck"], normalize="index"
        ) * 100
        div_bottlenecks = div_bottlenecks.round(1).reset_index()
        
        return {
            "divisions": div_summary.to_dict(orient="records"),
            "bottlenecks_by_division": div_bottlenecks.to_dict(orient="records")
        }

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_file = os.path.join(project_root, "data", "microsoft_workforce_productivity.csv")
    analyzer = ProductivityAnalyzer(data_file)
    kpis = analyzer.get_enterprise_kpis()
    print("KPIs:", kpis)
    curve = analyzer.analyze_overwork_paradox_curve()
    print(f"Optimal Peak Hours: {curve['optimal_peak_hours']} hrs/week")
    metrics = analyzer.train_ml_models()
    print("ML Metrics:", metrics)

