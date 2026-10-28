"""
Data Generator for Project - 07: Employee Productivity vs. Workload
Microsoft Corporation - Engineering & Operations Telemetry Simulator

Generates high-fidelity, empirically grounded telemetry records modeling the
'Overwork Paradox' and operational productivity bottlenecks observed by Microsoft Management.
"""

import os
import numpy as np
import pandas as pd

DIVISIONS = [
    "Azure Cloud Infrastructure",
    "Office 365 & M365 Copilot",
    "Developer Division & GitHub",
    "Windows & Modern Devices",
    "AI Platform & Research",
    "Customer & Enterprise Operations"
]

ROLES = [
    ("Principal Software Architect", 67, 0.08),
    ("Senior Software Engineer", 64, 0.22),
    ("Software Engineer II", 62, 0.30),
    ("Software Engineer I", 60, 0.15),
    ("Technical Program Manager", 63, 0.10),
    ("Applied AI / Data Scientist", 64, 0.07),
    ("Site Reliability Engineer (SRE)", 62, 0.05),
    ("Customer Escalation Engineer", 60, 0.03)
]

def generate_telemetry_dataset(num_records=12500, random_state=42, output_dir=None):
    """
    Synthesizes enterprise telemetry capturing workload strain, overtime degradation,
    absenteeism friction, task velocity, Glint engagement, and operational bottlenecks.
    """
    np.random.seed(random_state)
    
    records = []
    
    role_names = [r[0] for r in ROLES]
    role_grades = {r[0]: r[1] for r in ROLES}
    role_probs = [r[2] for r in ROLES]
    
    for i in range(1, num_records + 1):
        emp_id = f"MSFT-{10000 + i}"
        division = np.random.choice(DIVISIONS, p=[0.26, 0.24, 0.18, 0.12, 0.12, 0.08])
        role = np.random.choice(role_names, p=role_probs)
        grade = role_grades[role] + int(np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2]))
        tenure = round(float(np.random.gamma(shape=2.5, scale=2.0)), 1)
        tenure = min(max(tenure, 0.4), 22.0)
        
        # Division-specific workload bias (Azure and AI have heavier crunch cycles)
        div_strain_bias = {
            "Azure Cloud Infrastructure": 1.12,
            "Office 365 & M365 Copilot": 1.08,
            "Developer Division & GitHub": 0.98,
            "Windows & Modern Devices": 1.02,
            "AI Platform & Research": 1.15,
            "Customer & Enterprise Operations": 0.95
        }[division]
        
        # Base weekly working hours (Contracted = 40.0)
        # Latent workload pressure distribution: Bimodal (Standard workers vs Overworked crunch)
        is_crunch_cohort = np.random.rand() < (0.38 * div_strain_bias)
        if is_crunch_cohort:
            base_hours = np.random.normal(loc=54.5 * div_strain_bias, scale=6.2)
        else:
            base_hours = np.random.normal(loc=41.5, scale=3.5)
            
        weekly_hours = round(float(np.clip(base_hours, 36.0, 72.0)), 1)
        contracted_hours = 40.0
        overtime_hours = round(max(0.0, weekly_hours - contracted_hours), 1)
        
        # Weekend and After-hours patterns
        weekend_prob = min(0.90, max(0.05, (weekly_hours - 40.0) / 32.0))
        weekend_hours = round(float(np.random.exponential(scale=2.8)) if np.random.rand() < weekend_prob else 0.0, 1)
        weekend_hours = min(weekend_hours, 14.0)
        
        after_hours_pings = int(np.clip(
            np.random.poisson(lam=(overtime_hours * 2.8 + weekend_hours * 3.5 + 4)),
            0, 180
        ))
        
        # Meeting Overload & Fragmentation
        # TPMs and Principal Architects face severe meeting load
        role_meeting_mult = 1.6 if "Program Manager" in role else (1.4 if "Principal" in role else 1.0)
        daily_meeting_hours = round(float(np.clip(
            np.random.normal(loc=(2.4 + (weekly_hours - 40) * 0.08) * role_meeting_mult, scale=0.8),
            0.8, 7.2
        )), 1)
        weekly_meeting_hours = round(daily_meeting_hours * 5.0, 1)
        
        # Focus Time Blocks (Uninterrupted hours for deep engineering work)
        # Squeezed severely by high meeting hours and after-hours pings
        potential_focus = max(1.0, weekly_hours - weekly_meeting_hours - 10.0)
        focus_time_hours = round(float(np.clip(
            potential_focus * np.random.uniform(0.35, 0.75) / (1.0 + (after_hours_pings / 60.0)),
            1.5, 32.0
        )), 1)
        
        # Context Switching Index (Scale 1.0 - 10.0)
        context_switching_score = round(float(np.clip(
            2.0 + (weekly_meeting_hours / 5.0) * 0.9 + (after_hours_pings / 25.0) * 0.6 + np.random.normal(0, 0.4),
            1.0, 10.0
        )), 1)
        
        # Task Backlog & Story Points
        base_points = 28 if "Senior" in role or "Principal" in role else 20
        story_points_planned = int(np.clip(
            np.random.normal(loc=base_points * (weekly_hours / 40.0) * 1.1, scale=6.0),
            10, 65
        ))
        active_ticket_count = int(np.clip(
            np.random.poisson(lam=(story_points_planned / 3.0) + (context_switching_score * 0.8)),
            3, 32
        ))
        
        # Cognitive Fatigue Index (Scale 0 - 100)
        # Surges non-linearly when hours exceed 45 and focus time is low
        hours_diff = max(0.0, weekly_hours - 42.0)
        hours_exhaustion_penalty = (hours_diff ** 1.35) * 2.1
        meeting_exhaustion = (weekly_meeting_hours / 35.0) * 25.0
        switching_exhaustion = (context_switching_score / 10.0) * 20.0
        fatigue_noise = np.random.normal(0, 4.0)
        cognitive_fatigue_index = round(float(np.clip(
            15.0 + hours_exhaustion_penalty + meeting_exhaustion + switching_exhaustion + fatigue_noise,
            5.0, 100.0
        )), 1)
        
        # Glint Engagement Scores (Microsoft Glint scale 1.0 - 5.0)
        glint_wlb = round(float(np.clip(
            5.2 - (cognitive_fatigue_index / 22.0) + np.random.normal(0, 0.25),
            1.0, 5.0
        )), 2)
        glint_manager = round(float(np.clip(
            4.2 - (0.015 * after_hours_pings) + np.random.normal(0, 0.35),
            1.0, 5.0
        )), 2)
        glint_autonomy = round(float(np.clip(
            4.4 - (weekly_meeting_hours / 25.0) + np.random.normal(0, 0.3),
            1.0, 5.0
        )), 2)
        
        # Absenteeism Metrics (Quarterly)
        # Burnout-induced sick leaves spike when fatigue > 65
        sick_days_base = 1.2 + (cognitive_fatigue_index / 18.0) ** 1.4
        unplanned_sick_days = int(np.clip(
            np.random.poisson(lam=sick_days_base),
            0, 16
        ))
        burnout_absenteeism_episodes = int(np.clip(
            (cognitive_fatigue_index - 50.0) / 15.0 + np.random.poisson(0.4) if cognitive_fatigue_index > 50 else 0,
            0, 6
        ))
        
        # Task Completion & Velocity Decay (The Overwork Paradox!)
        # As weekly hours cross ~42-45 hrs, marginal efficiency declines;
        # beyond 52 hrs, error rates double, rework spikes, net points completed drops!
        if weekly_hours <= 42.0:
            efficiency_factor = 1.0 + (weekly_hours - 40.0) * 0.015
        elif weekly_hours <= 50.0:
            efficiency_factor = 1.03 - ((weekly_hours - 42.0) * 0.025)
        elif weekly_hours <= 60.0:
            efficiency_factor = 0.83 - ((weekly_hours - 50.0) * 0.040)
        else: # Severe overwork collapse
            efficiency_factor = 0.43 - ((weekly_hours - 60.0) * 0.035)
            
        efficiency_factor = max(0.20, efficiency_factor)
        
        # Deduct further for context switching & meeting overload
        efficiency_factor *= (1.0 - (context_switching_score / 35.0))
        efficiency_factor = max(0.18, efficiency_factor)
        
        raw_completed = story_points_planned * efficiency_factor * np.random.normal(1.0, 0.08)
        story_points_completed = int(np.clip(raw_completed, 4, story_points_planned + 4))
        
        task_completion_rate = round(float(min(1.15, story_points_completed / max(1, story_points_planned))), 3)
        sprint_spillover_rate = round(float(max(0.0, 1.0 - task_completion_rate)), 3)
        
        # Quality & Rework Telemetry
        # Cognitive fatigue creates bug re-openings and code churn
        pr_cycle_base = 18.0 + (weekly_meeting_hours * 1.5) + (context_switching_score * 4.2)
        pr_cycle_time_hours = round(float(np.clip(
            pr_cycle_base * (1.0 + (cognitive_fatigue_index / 80.0)) + np.random.normal(0, 4.0),
            6.0, 168.0
        )), 1)
        
        bug_reopen_rate = round(float(np.clip(
            4.0 + (cognitive_fatigue_index / 3.0) + (overtime_hours * 0.6) + np.random.normal(0, 2.5),
            2.0, 48.0
        )), 1)
        
        code_churn_rework_pct = round(float(np.clip(
            6.0 + (bug_reopen_rate * 0.85) + (context_switching_score * 2.0) + np.random.normal(0, 3.0),
            4.0, 62.0
        )), 1)
        
        # Effective Productivity Index (EPI: Scale 0 - 100)
        # Represents true net value created per unit time:
        # High raw hours with high churn/bugs and low completion results in poor EPI!
        raw_velocity_score = (story_points_completed / 30.0) * 40.0
        quality_score = max(0.0, 35.0 - (bug_reopen_rate * 0.45) - (code_churn_rework_pct * 0.25))
        engagement_bonus = (glint_wlb / 5.0) * 15.0
        fatigue_drag = (cognitive_fatigue_index / 100.0) * 20.0
        absenteeism_drag = (unplanned_sick_days / 15.0) * 12.0
        
        effective_productivity_index = round(float(np.clip(
            raw_velocity_score + quality_score + engagement_bonus - fatigue_drag - absenteeism_drag + 10.0,
            12.0, 98.5
        )), 1)
        
        # Annual Salary Estimate (USD) for economic quantification
        salary_map = {
            "Principal Software Architect": 265000,
            "Senior Software Engineer": 195000,
            "Software Engineer II": 155000,
            "Software Engineer I": 120000,
            "Technical Program Manager": 175000,
            "Applied AI / Data Scientist": 190000,
            "Site Reliability Engineer (SRE)": 160000,
            "Customer Escalation Engineer": 115000
        }
        annual_salary = salary_map[role] + int(tenure * 2500)
        
        # Productivity Loss in USD:
        # Value lost due to sub-optimal productivity relative to benchmark potential
        potential_benchmark_epi = 85.0
        productivity_gap = max(0.0, (potential_benchmark_epi - effective_productivity_index) / 100.0)
        productivity_loss_usd = round(annual_salary * productivity_gap * 0.75, 2)
        
        # Operational Bottleneck Diagnostics & Intervention Assignment
        bottleneck, intervention = diagnose_bottleneck_and_intervention(
            weekly_hours=weekly_hours,
            weekly_meeting_hours=weekly_meeting_hours,
            focus_time_hours=focus_time_hours,
            context_switching_score=context_switching_score,
            cognitive_fatigue_index=cognitive_fatigue_index,
            unplanned_sick_days=unplanned_sick_days,
            bug_reopen_rate=bug_reopen_rate,
            code_churn_rework_pct=code_churn_rework_pct,
            story_points_planned=story_points_planned,
            active_ticket_count=active_ticket_count,
            effective_productivity_index=effective_productivity_index
        )
        
        records.append({
            "employee_id": emp_id,
            "division": division,
            "role": role,
            "level_grade": grade,
            "tenure_years": tenure,
            "contracted_hours": contracted_hours,
            "weekly_hours": weekly_hours,
            "overtime_hours": overtime_hours,
            "weekend_hours": weekend_hours,
            "after_hours_teams_pings": after_hours_pings,
            "daily_meeting_hours": daily_meeting_hours,
            "weekly_meeting_hours": weekly_meeting_hours,
            "focus_time_hours": focus_time_hours,
            "context_switching_score": context_switching_score,
            "active_ticket_count": active_ticket_count,
            "story_points_planned": story_points_planned,
            "story_points_completed": story_points_completed,
            "task_completion_rate": task_completion_rate,
            "sprint_spillover_rate": sprint_spillover_rate,
            "pr_cycle_time_hours": pr_cycle_time_hours,
            "bug_reopen_rate": bug_reopen_rate,
            "code_churn_rework_pct": code_churn_rework_pct,
            "unplanned_sick_days": unplanned_sick_days,
            "burnout_absenteeism_episodes": burnout_absenteeism_episodes,
            "glint_work_life_balance": glint_wlb,
            "glint_manager_support": glint_manager,
            "glint_empowerment_autonomy": glint_autonomy,
            "cognitive_fatigue_index": cognitive_fatigue_index,
            "effective_productivity_index": effective_productivity_index,
            "annual_salary": annual_salary,
            "productivity_loss_usd": productivity_loss_usd,
            "primary_bottleneck": bottleneck,
            "intervention_recommendation": intervention
        })
        
    df = pd.DataFrame(records)
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        csv_path = os.path.join(output_dir, "microsoft_workforce_productivity.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved {len(df):,} workforce records to {csv_path}")
        
        # Also create divisional aggregates
        div_agg = df.groupby("division").agg({
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
        
        agg_path = os.path.join(output_dir, "microsoft_divisional_aggregates.csv")
        div_agg.to_csv(agg_path, index=False)
        print(f"Saved divisional aggregates to {agg_path}")
        
    return df

def diagnose_bottleneck_and_intervention(
    weekly_hours, weekly_meeting_hours, focus_time_hours, context_switching_score,
    cognitive_fatigue_index, unplanned_sick_days, bug_reopen_rate,
    code_churn_rework_pct, story_points_planned, active_ticket_count,
    effective_productivity_index
):
    """
    Expert rule-based logic to categorize primary bottleneck and targeted intervention.
    """
    # 1. Meeting & Collaboration Fragmentation
    if weekly_meeting_hours >= 18.0 or (focus_time_hours < 8.0 and context_switching_score >= 6.5):
        return (
            "Meeting & Collaboration Fragmentation",
            "Enforce 'No-Meeting Wednesdays', limit recurring syncs to 25 mins, and establish 4-hour daily Focus Time shields."
        )
    # 2. Chronic Overtime & Cognitive Exhaustion
    elif weekly_hours >= 50.0 or cognitive_fatigue_index >= 68.0:
        return (
            "Chronic Overtime & Cognitive Exhaustion",
            "Institute strict 45-hour weekly cap, enforce 48-hour post-incident cooldowns, and implement Glint fatigue tripwires."
        )
    # 3. Rework Loops & Technical Debt Quagmire
    elif bug_reopen_rate >= 22.0 or code_churn_rework_pct >= 32.0:
        return (
            "Rework Loops & Technical Debt Quagmire",
            "Mandate dedicated 20% Tech-Debt sprint capacity, automated CI/CD gating, and senior architectural pair reviews."
        )
    # 4. Capacity Instability & Absenteeism Cascade
    elif unplanned_sick_days >= 6 or cognitive_fatigue_index >= 60.0 and unplanned_sick_days >= 4:
        return (
            "Capacity Instability & Absenteeism Cascade",
            "Trigger Manager Support 1-on-1s, introduce asynchronous sprint handoffs, and offer flexible wellness recovery cycles."
        )
    # 5. Asymmetric Workload Overburden
    elif story_points_planned >= 44 or active_ticket_count >= 18:
        return (
            "Asymmetric Workload Overburden",
            "Rebalance sprint backlog, cap concurrent work-in-progress (WIP) to 3 items, and redistribute tickets to junior engineers."
        )
    # 6. Optimal / Balanced Throughput
    else:
        return (
            "Optimal / Balanced Throughput",
            "Maintain current equilibrium; leverage team members as mentors and benchmarks for sustainable engineering practices."
        )

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    generate_telemetry_dataset(num_records=12500, output_dir=out_dir)
