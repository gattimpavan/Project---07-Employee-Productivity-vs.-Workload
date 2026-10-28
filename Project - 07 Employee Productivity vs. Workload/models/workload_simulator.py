"""
Workload & Policy Intervention Simulator
Project - 07: Employee Productivity vs. Workload
Microsoft Corporation - Predictive Workload Optimization System
"""

import numpy as np
import pandas as pd

class WorkloadSimulator:
    def __init__(self, df, reg_model=None, feature_names=None):
        self.df = df.copy()
        self.reg_model = reg_model
        self.feature_names = feature_names
        
    def run_simulation(
        self,
        meeting_reduction_pct=25.0,
        max_overtime_cap_hours=45.0,
        focus_time_shield_days=1.5,
        backlog_rebalance_factor=20.0
    ):
        """
        Simulates organizational productivity, quality, and financial outcomes
        under customized workload intervention policies.
        """
        sim_df = self.df.copy()
        
        # 1. Cap weekly hours
        sim_df["sim_weekly_hours"] = sim_df["weekly_hours"].apply(lambda h: min(h, float(max_overtime_cap_hours)))
        sim_df["sim_overtime_hours"] = sim_df["sim_weekly_hours"].apply(lambda h: max(0.0, h - 40.0))
        
        # 2. Reduce meeting hours
        reduction_ratio = max(0.0, min(0.60, meeting_reduction_pct / 100.0))
        sim_df["sim_meeting_hours"] = sim_df["weekly_meeting_hours"] * (1.0 - reduction_ratio)
        
        # 3. Boost focus time
        focus_boost = focus_time_shield_days * 3.2
        sim_df["sim_focus_time_hours"] = np.clip(sim_df["focus_time_hours"] + focus_boost, 2.0, 35.0)
        
        # 4. Decrease context switching
        switch_relief = (reduction_ratio * 2.5) + (focus_time_shield_days * 0.8)
        sim_df["sim_context_switching"] = np.clip(sim_df["context_switching_score"] - switch_relief, 1.2, 10.0)
        
        # 5. Cognitive Fatigue Index Relief
        fatigue_reduction = (
            (sim_df["weekly_hours"] - sim_df["sim_weekly_hours"]) * 2.2 +
            (sim_df["weekly_meeting_hours"] - sim_df["sim_meeting_hours"]) * 1.4 +
            (focus_boost * 1.1)
        )
        sim_df["sim_cognitive_fatigue"] = np.clip(sim_df["cognitive_fatigue_index"] - fatigue_reduction, 8.0, 100.0)
        
        # 6. Improved Glint Work-Life Balance
        sim_df["sim_glint_wlb"] = np.clip(sim_df["glint_work_life_balance"] + (fatigue_reduction / 24.0), 1.0, 4.95)
        
        # 7. Unplanned Sick Days reduction
        sim_df["sim_sick_days"] = np.clip(
            sim_df["unplanned_sick_days"] - (fatigue_reduction / 15.0).round(),
            0.0, 16.0
        )
        
        # 8. Rebalance Backlog & Task Completion
        rebal_ratio = backlog_rebalance_factor / 100.0
        sim_df["sim_story_points_planned"] = sim_df["story_points_planned"] * (1.0 - rebal_ratio * 0.4)
        
        # Task completion rate improves substantially
        completion_gain = 0.12 + (reduction_ratio * 0.18) + (rebal_ratio * 0.15)
        sim_df["sim_task_completion_rate"] = np.clip(sim_df["task_completion_rate"] + completion_gain, 0.40, 1.0)
        sim_df["sim_sprint_spillover_rate"] = np.clip(1.0 - sim_df["sim_task_completion_rate"], 0.0, 0.60)
        
        # 9. Quality & Rework Improvement
        bug_drop = (fatigue_reduction * 0.35) + (reduction_ratio * 6.0)
        sim_df["sim_bug_reopen_rate"] = np.clip(sim_df["bug_reopen_rate"] - bug_drop, 3.0, 45.0)
        sim_df["sim_code_churn_pct"] = np.clip(sim_df["code_churn_rework_pct"] - (bug_drop * 0.8), 4.0, 50.0)
        
        # 10. Re-calculate Effective Productivity Index (EPI)
        # Using analytical simulation model
        epi_gain = (
            (sim_df["sim_task_completion_rate"] - sim_df["task_completion_rate"]) * 35.0 +
            (sim_df["bug_reopen_rate"] - sim_df["sim_bug_reopen_rate"]) * 0.45 +
            (sim_df["cognitive_fatigue_index"] - sim_df["sim_cognitive_fatigue"]) * 0.22 +
            (sim_df["sim_glint_wlb"] - sim_df["glint_work_life_balance"]) * 4.0
        )
        sim_df["sim_effective_productivity_index"] = np.clip(
            sim_df["effective_productivity_index"] + epi_gain,
            20.0, 96.0
        )
        
        # 11. Economic Impact
        benchmark_epi = 85.0
        orig_gap = np.clip((benchmark_epi - sim_df["effective_productivity_index"]) / 100.0, 0.0, 1.0)
        new_gap = np.clip((benchmark_epi - sim_df["sim_effective_productivity_index"]) / 100.0, 0.0, 1.0)
        
        orig_loss = sim_df["productivity_loss_usd"].sum()
        sim_loss = (sim_df["annual_salary"] * new_gap * 0.75).sum()
        net_savings_usd = max(0.0, orig_loss - sim_loss)
        
        # Aggregate baseline vs simulated
        baseline = {
            "avg_weekly_hours": round(float(self.df["weekly_hours"].mean()), 1),
            "avg_meeting_hours": round(float(self.df["weekly_meeting_hours"].mean()), 1),
            "avg_focus_time": round(float(self.df["focus_time_hours"].mean()), 1),
            "avg_task_completion_pct": round(float(self.df["task_completion_rate"].mean() * 100), 1),
            "avg_sprint_spillover_pct": round(float(self.df["sprint_spillover_rate"].mean() * 100), 1),
            "avg_bug_reopen_rate": round(float(self.df["bug_reopen_rate"].mean()), 1),
            "avg_cognitive_fatigue": round(float(self.df["cognitive_fatigue_index"].mean()), 1),
            "avg_glint_wlb": round(float(self.df["glint_work_life_balance"].mean()), 2),
            "avg_sick_days": round(float(self.df["unplanned_sick_days"].mean()), 1),
            "avg_effective_productivity_index": round(float(self.df["effective_productivity_index"].mean()), 1),
            "total_productivity_loss_millions": round(float(orig_loss / 1e6), 1)
        }
        
        simulated = {
            "avg_weekly_hours": round(float(sim_df["sim_weekly_hours"].mean()), 1),
            "avg_meeting_hours": round(float(sim_df["sim_meeting_hours"].mean()), 1),
            "avg_focus_time": round(float(sim_df["sim_focus_time_hours"].mean()), 1),
            "avg_task_completion_pct": round(float(sim_df["sim_task_completion_rate"].mean() * 100), 1),
            "avg_sprint_spillover_pct": round(float(sim_df["sim_sprint_spillover_rate"].mean() * 100), 1),
            "avg_bug_reopen_rate": round(float(sim_df["sim_bug_reopen_rate"].mean()), 1),
            "avg_cognitive_fatigue": round(float(sim_df["sim_cognitive_fatigue"].mean()), 1),
            "avg_glint_wlb": round(float(sim_df["sim_glint_wlb"].mean()), 2),
            "avg_sick_days": round(float(sim_df["sim_sick_days"].mean()), 1),
            "avg_effective_productivity_index": round(float(sim_df["sim_effective_productivity_index"].mean()), 1),
            "total_productivity_loss_millions": round(float(sim_loss / 1e6), 1)
        }
        
        delta = {
            "productivity_lift_pct": round(float(simulated["avg_effective_productivity_index"] - baseline["avg_effective_productivity_index"]), 1),
            "task_completion_improvement_pct": round(float(simulated["avg_task_completion_pct"] - baseline["avg_task_completion_pct"]), 1),
            "sprint_spillover_reduction_pct": round(float(baseline["avg_sprint_spillover_pct"] - simulated["avg_sprint_spillover_pct"]), 1),
            "meeting_hours_reclaimed_weekly": round(float(baseline["avg_meeting_hours"] - simulated["avg_meeting_hours"]), 1),
            "focus_hours_gained_weekly": round(float(simulated["avg_focus_time"] - baseline["avg_focus_time"]), 1),
            "bug_reopen_reduction_pct": round(float(baseline["avg_bug_reopen_rate"] - simulated["avg_bug_reopen_rate"]), 1),
            "sick_days_averted_quarterly": round(float(baseline["avg_sick_days"] - simulated["avg_sick_days"]), 1),
            "net_financial_savings_millions": round(float(net_savings_usd / 1e6), 1)
        }
        
        return {
            "policy_parameters": {
                "meeting_reduction_pct": meeting_reduction_pct,
                "max_overtime_cap_hours": max_overtime_cap_hours,
                "focus_time_shield_days": focus_time_shield_days,
                "backlog_rebalance_factor": backlog_rebalance_factor
            },
            "baseline": baseline,
            "simulated": simulated,
            "delta": delta
        }

if __name__ == "__main__":
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_file = os.path.join(project_root, "data", "microsoft_workforce_productivity.csv")
    df = pd.read_csv(data_file)
    sim = WorkloadSimulator(df)
    res = sim.run_simulation()
    print("Simulation Results:", res["delta"])

