"""
Data utilities and caching for Bodycote Command Centre
"""

import streamlit as st
from data.generate_demo_data import generate_all_data
import pandas as pd
import numpy as np
from datetime import datetime


@st.cache_resource
def get_data():
    """Get or generate cached demo data"""
    return generate_all_data()


def get_sites():
    """Get sites dataframe"""
    return get_data()["sites"]


def get_customers():
    """Get customers dataframe"""
    return get_data()["customers"]


def get_furnaces():
    """Get furnaces dataframe"""
    return get_data()["furnaces"]


def get_orders():
    """Get orders dataframe"""
    return get_data()["orders"]


def get_daily_metrics():
    """Get daily metrics dataframe"""
    return get_data()["daily_metrics"]


def get_complaints():
    """Get complaints dataframe"""
    return get_data()["complaints"]


def get_maintenance():
    """Get maintenance dataframe"""
    return get_data()["maintenance"]


def get_mtd_revenue(site_id=None):
    """Calculate month-to-date revenue"""
    orders = get_orders()
    today = pd.Timestamp.today()
    current_month_start = today.replace(day=1).date()
    
    month_orders = orders[orders["completion_date"].notna()]
    month_orders["completion_date"] = pd.to_datetime(month_orders["completion_date"]).dt.date
    month_orders = month_orders[month_orders["completion_date"] >= current_month_start]
    
    if site_id:
        month_orders = month_orders[month_orders["site_id"] == site_id]
    
    return month_orders["revenue"].sum()


def get_ytd_revenue(site_id=None):
    """Calculate year-to-date revenue"""
    orders = get_orders()
    today = pd.Timestamp.today()
    current_year_start = today.replace(month=1, day=1).date()
    
    year_orders = orders[orders["completion_date"].notna()]
    year_orders["completion_date"] = pd.to_datetime(year_orders["completion_date"]).dt.date
    year_orders = year_orders[year_orders["completion_date"] >= current_year_start]
    
    if site_id:
        year_orders = year_orders[year_orders["site_id"] == site_id]
    
    return year_orders["revenue"].sum()


def get_orders_running(site_id=None):
    """Get count of running orders"""
    orders = get_orders()
    running = orders[orders["status"] == "In Progress"]
    
    if site_id:
        running = running[running["site_id"] == site_id]
    
    return len(running)


def get_on_time_delivery_pct(site_id=None):
    """Calculate on-time delivery percentage"""
    orders = get_orders()
    completed = orders[orders["status"] == "Completed"]
    
    if site_id:
        completed = completed[completed["site_id"] == site_id]
    
    if len(completed) == 0:
        return 0
    
    completed = completed.copy()
    completed["completion_date"] = pd.to_datetime(completed["completion_date"]).dt.date
    completed["due_date"] = pd.to_datetime(completed["due_date"]).dt.date
    on_time = completed[completed["completion_date"] <= completed["due_date"]]
    return (len(on_time) / len(completed)) * 100


def get_first_pass_yield(site_id=None):
    """Calculate first pass yield percentage"""
    orders = get_orders()
    completed = orders[orders["status"] == "Completed"]
    
    if site_id:
        completed = completed[completed["site_id"] == site_id]
    
    if len(completed) == 0:
        return 0
    
    passed = completed[completed["quality_result"] == "Pass"]
    return (len(passed) / len(completed)) * 100


def get_furnace_utilisation(site_id=None):
    """Calculate average furnace utilisation"""
    metrics = get_daily_metrics()
    cutoff_date = (pd.Timestamp.today() - pd.Timedelta(days=30)).date()
    metrics["date"] = pd.to_datetime(metrics["date"]).dt.date
    recent_metrics = metrics[metrics["date"] >= cutoff_date]
    
    if site_id:
        recent_metrics = recent_metrics[recent_metrics["site_id"] == site_id]
    
    if len(recent_metrics) == 0:
        return 0
    
    return recent_metrics["utilisation"].mean()


def get_gross_margin(site_id=None):
    """Calculate gross margin percentage"""
    orders = get_orders()
    completed = orders[orders["status"] == "Completed"]
    
    if site_id:
        completed = completed[completed["site_id"] == site_id]
    
    total_revenue = completed["revenue"].sum()
    total_cost = completed["cost"].sum()
    
    if total_revenue == 0:
        return 0
    
    return ((total_revenue - total_cost) / total_revenue) * 100


def get_safety_incidents(site_id=None):
    """Get safety incidents count (last 30 days)"""
    metrics = get_daily_metrics()
    cutoff_date = (pd.Timestamp.today() - pd.Timedelta(days=30)).date()
    metrics["date"] = pd.to_datetime(metrics["date"]).dt.date
    recent = metrics[metrics["date"] >= cutoff_date]
    
    if site_id:
        recent = recent[recent["site_id"] == site_id]
    
    return int(recent["safety_incidents"].sum())


def get_complaints_count(days=30):
    """Get complaints count"""
    complaints = get_complaints()
    complaints["date_raised"] = pd.to_datetime(complaints["date_raised"]).dt.date
    cutoff_date = (pd.Timestamp.today() - pd.Timedelta(days=days)).date()
    recent = complaints[complaints["date_raised"] >= cutoff_date]
    return len(recent)


def get_customer_revenue(customer_id=None):
    """Get customer revenue"""
    orders = get_orders()
    completed = orders[orders["status"] == "Completed"]
    
    if customer_id:
        completed = completed[completed["customer_id"] == customer_id]
    
    return completed["revenue"].sum()


def get_revenue_by_process():
    """Get revenue and margin breakdown by process"""
    orders = get_orders()
    completed = orders[orders["status"] == "Completed"]
    if completed.empty:
        return pd.DataFrame(columns=["process", "revenue", "gross_margin_pct"])

    grouped = (
        completed.groupby("process", as_index=False)
        .agg(revenue=("revenue", "sum"), cost=("cost", "sum"))
    )
    grouped["gross_margin_pct"] = grouped.apply(
        lambda row: ((row["revenue"] - row["cost"]) / row["revenue"] * 100) if row["revenue"] else 0,
        axis=1,
    )
    return grouped.sort_values("revenue", ascending=False)[["process", "revenue", "gross_margin_pct"]]


def get_revenue_by_region():
    """Get revenue breakdown by region"""
    orders = get_orders()
    sites = get_sites()
    completed = orders[orders["status"] == "Completed"]

    if completed.empty:
        return pd.DataFrame(columns=["region", "revenue"])

    # Merge with sites to get region
    completed = completed.merge(sites[["site_id", "region"]], on="site_id")
    grouped = completed.groupby("region", as_index=False)["revenue"].sum()
    return grouped.sort_values("revenue", ascending=False)


def get_revenue_trend(days=90):
    """Get daily revenue trend"""
    metrics = get_daily_metrics()
    cutoff_date = (pd.Timestamp.today() - pd.Timedelta(days=days)).date()
    metrics["date"] = pd.to_datetime(metrics["date"]).dt.date
    recent = metrics[metrics["date"] >= cutoff_date]
    daily_revenue = recent.groupby("date")["revenue"].sum().reset_index()
    return daily_revenue.sort_values("date")


def get_top_customers(n=10):
    """Get top customers by revenue"""
    orders = get_orders()
    completed = orders[orders["status"] == "Completed"]
    customer_revenue = completed.groupby("customer_id")["revenue"].sum().sort_values(ascending=False).head(n)
    
    customers = get_customers()
    result = []
    for cust_id, revenue in customer_revenue.items():
        cust_name = customers[customers["customer_id"] == cust_id]["customer_name"].values
        if len(cust_name) > 0:
            result.append({"customer_id": cust_id, "customer_name": cust_name[0], "revenue": revenue})
    
    return pd.DataFrame(result)


def get_site_performance():
    """Get site performance metrics"""
    sites = get_sites()
    performance = []
    site_name_col = "site_name" if "site_name" in sites.columns else "name" if "name" in sites.columns else None
    
    for _, site in sites.iterrows():
        revenue = get_ytd_revenue(site["site_id"])
        utilisation = get_furnace_utilisation(site["site_id"])
        on_time = get_on_time_delivery_pct(site["site_id"])
        fpy = get_first_pass_yield(site["site_id"])
        
        performance.append({
            "site_id": site["site_id"],
            "site_name": site[site_name_col] if site_name_col else site["site_id"],
            "region": site["region"] if "region" in site.index else "Unknown",
            "revenue": revenue,
            "utilisation": utilisation,
            "on_time_delivery": on_time,
            "first_pass_yield": fpy,
        })
    
    return pd.DataFrame(performance)


def _safe_dataset(name: str) -> pd.DataFrame:
    data = get_data()
    frame = data.get(name)
    if isinstance(frame, pd.DataFrame):
        return frame.copy()
    return pd.DataFrame()


def get_workforce_employees() -> pd.DataFrame:
    return _safe_dataset("workforce_employees")


def get_workforce_absence() -> pd.DataFrame:
    return _safe_dataset("workforce_absence")


def get_workforce_recruitment() -> pd.DataFrame:
    return _safe_dataset("workforce_recruitment")


def get_workforce_safety() -> pd.DataFrame:
    return _safe_dataset("workforce_safety")


def get_workforce_daily() -> pd.DataFrame:
    wf = _safe_dataset("workforce_daily")
    if wf.empty:
        # Keep schema-stable empty frame for downstream grouping/sorting.
        return pd.DataFrame(columns=["date"])
    if "date" not in wf.columns:
        return pd.DataFrame(columns=["date"])
    wf["date"] = pd.to_datetime(wf["date"], errors="coerce")
    return wf.dropna(subset=["date"])


def _window(df: pd.DataFrame, days: int) -> pd.DataFrame:
    if df.empty or "date" not in df.columns:
        return df
    cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=days)
    return df[df["date"] >= cutoff].copy()


def _previous_window(df: pd.DataFrame, days: int) -> pd.DataFrame:
    if df.empty or "date" not in df.columns:
        return df
    end = pd.Timestamp.today().normalize() - pd.Timedelta(days=days)
    start = end - pd.Timedelta(days=days)
    return df[(df["date"] >= start) & (df["date"] < end)].copy()


def _safe_mean(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return float(series.fillna(0).mean())


def _safe_sum(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return float(series.fillna(0).sum())


def _change_pct(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / abs(previous)) * 100


def _status_by_target(current: float, target: float, higher_is_better: bool = True, tolerance: float = 0.0) -> str:
    if higher_is_better:
        if current >= target:
            return "success"
        if current >= (target - tolerance):
            return "warning"
        return "critical"
    if current <= target:
        return "success"
    if current <= (target + tolerance):
        return "warning"
    return "critical"


def get_workforce_kpi_pack() -> list[dict]:
    employees = get_workforce_employees()
    absence = get_workforce_absence()
    recruit = get_workforce_recruitment()
    safety = get_workforce_safety()
    wf_daily = get_workforce_daily()
    orders = get_orders().copy()

    active = employees[employees["termination_date"].isna()].copy() if not employees.empty else pd.DataFrame()
    total_employees = float(len(employees))
    current_headcount = float(len(active))
    open_vacancies = float(len(recruit[recruit["status"] == "Open"])) if not recruit.empty else 0.0
    vacancy_rate = (open_vacancies / max(current_headcount + open_vacancies, 1)) * 100

    term = employees[employees["termination_date"].notna()].copy() if not employees.empty else pd.DataFrame()
    term["termination_date"] = pd.to_datetime(term.get("termination_date"), errors="coerce")
    recent_leavers = float(len(term[term["termination_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=30))])) if not term.empty else 0.0
    prev_leavers = float(len(term[(term["termination_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=60))) & (term["termination_date"] < (pd.Timestamp.today().normalize() - pd.Timedelta(days=30)))])) if not term.empty else 0.0
    turnover = (recent_leavers / max(current_headcount, 1)) * 100
    prev_turnover = (prev_leavers / max(current_headcount, 1)) * 100
    retention = 100 - turnover
    prev_retention = 100 - prev_turnover

    recent_wf = _window(wf_daily, 30)
    prev_wf = _previous_window(wf_daily, 30)
    absence_rate = _safe_mean(recent_wf.get("absence_rate", pd.Series(dtype=float)))
    prev_absence_rate = _safe_mean(prev_wf.get("absence_rate", pd.Series(dtype=float)))
    overtime_hours = _safe_mean(recent_wf.get("overtime_hours", pd.Series(dtype=float)))
    prev_overtime = _safe_mean(prev_wf.get("overtime_hours", pd.Series(dtype=float)))
    labour_cost_mtd = _safe_sum(recent_wf.get("labour_cost", pd.Series(dtype=float)))
    prev_labour_cost = _safe_sum(prev_wf.get("labour_cost", pd.Series(dtype=float)))
    budget_mtd = labour_cost_mtd * 0.96
    labour_vs_budget = ((labour_cost_mtd - budget_mtd) / max(budget_mtd, 1)) * 100

    orders_done = orders[orders["status"] == "Completed"] if "status" in orders.columns else orders
    orders_done["completion_date"] = pd.to_datetime(orders_done.get("completion_date"), errors="coerce")
    recent_orders = orders_done[orders_done["completion_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=30))]
    prev_orders = orders_done[(orders_done["completion_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=60))) & (orders_done["completion_date"] < (pd.Timestamp.today().normalize() - pd.Timedelta(days=30)))]

    rev_recent = _safe_sum(recent_orders.get("revenue", pd.Series(dtype=float)))
    rev_prev = _safe_sum(prev_orders.get("revenue", pd.Series(dtype=float)))
    rev_per_employee = rev_recent / max(current_headcount, 1)
    prev_rev_per_employee = rev_prev / max(current_headcount, 1)

    orders_per_employee = float(len(recent_orders) / max(current_headcount, 1))
    prev_orders_per_employee = float(len(prev_orders) / max(current_headcount, 1))

    training_compliance = 0.0
    if not active.empty and "training_status" in active.columns:
        training_compliance = float((active["training_status"] == "Compliant").mean() * 100)
    prev_training = max(0.0, training_compliance - np.random.uniform(0.4, 1.4))

    time_to_fill = _safe_mean(recruit["time_to_fill_days"].dropna()) if not recruit.empty and "time_to_fill_days" in recruit.columns else 0.0
    prev_ttf = max(0.0, time_to_fill + np.random.uniform(-3.0, 4.5))

    incidents = safety.copy()
    incidents["event_date"] = pd.to_datetime(incidents.get("event_date"), errors="coerce")
    recent_incidents = incidents[incidents["event_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=30))] if not incidents.empty else incidents
    prev_incidents = incidents[(incidents["event_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=60))) & (incidents["event_date"] < (pd.Timestamp.today().normalize() - pd.Timedelta(days=30)))] if not incidents.empty else incidents
    safety_incidents = float(len(recent_incidents[recent_incidents.get("event_type") == "Recordable"])) if not recent_incidents.empty else 0.0
    prev_safety_incidents = float(len(prev_incidents[prev_incidents.get("event_type") == "Recordable"])) if not prev_incidents.empty else 0.0
    lti = float(len(recent_incidents[recent_incidents.get("event_type") == "LTI"])) if not recent_incidents.empty else 0.0
    prev_lti = float(len(prev_incidents[prev_incidents.get("event_type") == "LTI"])) if not prev_incidents.empty else 0.0

    engagement = _safe_mean(active.get("engagement_score", pd.Series(dtype=float)))
    prev_engagement = max(0.0, engagement - np.random.uniform(-1.5, 2.1))

    def row(name, current, target, previous, higher_better, unit=""):
        change = _change_pct(current, previous)
        status = _status_by_target(current, target, higher_better, tolerance=abs(target) * 0.03)
        spark = [max(0.0, previous * 0.88), previous, (previous + current) / 2, current * 0.96, current]
        return {
            "name": name,
            "current": current,
            "target": target,
            "previous": previous,
            "change_pct": change,
            "trend": "up" if current >= previous else "down",
            "status": status,
            "spark": spark,
            "unit": unit,
        }

    return [
        row("Total Employees", total_employees, total_employees * 0.98, total_employees * 0.99, True),
        row("Current Headcount", current_headcount, current_headcount + 8, current_headcount * 0.99, True),
        row("Vacancy Rate", vacancy_rate, 4.0, max(0.1, vacancy_rate * 1.08), False, "%"),
        row("Staff Turnover", turnover, 2.0, max(0.1, prev_turnover), False, "%"),
        row("Employee Retention", retention, 96.0, max(0.1, prev_retention), True, "%"),
        row("Absence Rate", absence_rate, 3.2, max(0.1, prev_absence_rate), False, "%"),
        row("Average Overtime Hours", overtime_hours, 9.0, max(0.1, prev_overtime), False),
        row("Labour Cost (MTD)", labour_cost_mtd, budget_mtd, max(0.1, prev_labour_cost), False),
        row("Labour Cost vs Budget", labour_vs_budget, 0.0, labour_vs_budget - np.random.uniform(0.8, 2.3), False, "%"),
        row("Revenue per Employee", rev_per_employee, 22000.0, max(0.1, prev_rev_per_employee), True),
        row("Orders Completed per Employee", orders_per_employee, 2.8, max(0.1, prev_orders_per_employee), True),
        row("Training Compliance", training_compliance, 95.0, max(0.1, prev_training), True, "%"),
        row("Average Time to Fill Vacancies", time_to_fill, 38.0, max(0.1, prev_ttf), False),
        row("Safety Incidents", safety_incidents, 3.0, max(0.1, prev_safety_incidents), False),
        row("Lost Time Injuries", lti, 1.0, max(0.1, prev_lti), False),
        row("Employee Engagement Score", engagement, 78.0, max(0.1, prev_engagement), True),
    ]


def get_absence_analytics() -> dict:
    abs_df = get_workforce_absence()
    wf_daily = get_workforce_daily()
    sites = get_sites()[["site_id", "site_name", "region"]].copy()

    if abs_df.empty:
        return {"trend": pd.DataFrame(), "by_site": pd.DataFrame(), "by_department": pd.DataFrame(), "by_shift": pd.DataFrame(), "types": pd.DataFrame(), "reasons": pd.DataFrame(), "bradford": pd.DataFrame(), "cost_site": pd.DataFrame(), "threshold_sites": pd.DataFrame(), "kpi": {}}

    abs_df["absence_date"] = pd.to_datetime(abs_df["absence_date"], errors="coerce")
    abs_df["month"] = abs_df["absence_date"].dt.to_period("M").dt.to_timestamp()

    trend = abs_df.groupby("month", as_index=False).agg(lost_days=("lost_days", "sum"), absence_cost=("estimated_cost", "sum"), events=("absence_id", "count"))
    by_site = abs_df.groupby("site", as_index=False).agg(absence_rate=("lost_days", "sum"), absence_cost=("estimated_cost", "sum"), events=("absence_id", "count")).sort_values("absence_rate", ascending=False)
    by_department = abs_df.groupby("department", as_index=False)["lost_days"].sum().sort_values("lost_days", ascending=False)
    by_shift = abs_df.groupby("shift_pattern", as_index=False)["lost_days"].sum().sort_values("lost_days", ascending=False)
    types = abs_df.groupby("absence_type", as_index=False)["lost_days"].sum()
    reasons = abs_df.groupby("absence_reason", as_index=False)["lost_days"].sum().sort_values("lost_days", ascending=False).head(8)
    bradford = abs_df[["employee_id", "bradford_factor"]].copy()
    cost_site = abs_df.groupby("site", as_index=False)["estimated_cost"].sum().sort_values("estimated_cost", ascending=False)

    if not wf_daily.empty:
        recent = _window(wf_daily, 30)
        site_rates = recent.groupby("site_id", as_index=False)["absence_rate"].mean().merge(sites, on="site_id", how="left")
        threshold_sites = site_rates[site_rates["absence_rate"] > 4.0].sort_values("absence_rate", ascending=False)
        absence_rate = float(site_rates["absence_rate"].mean()) if not site_rates.empty else 0.0
    else:
        threshold_sites = pd.DataFrame(columns=["site_name", "absence_rate"])
        absence_rate = 0.0

    kpi = {
        "lost_days": float(abs_df["lost_days"].sum()),
        "absence_cost": float(abs_df["estimated_cost"].sum()),
        "absence_rate": absence_rate,
    }
    return {
        "trend": trend,
        "by_site": by_site,
        "by_department": by_department,
        "by_shift": by_shift,
        "types": types,
        "reasons": reasons,
        "bradford": bradford,
        "cost_site": cost_site,
        "threshold_sites": threshold_sites,
        "kpi": kpi,
    }


def get_turnover_analytics() -> dict:
    employees = get_workforce_employees()
    if employees.empty:
        return {"trend": pd.DataFrame(), "by_site": pd.DataFrame(), "by_department": pd.DataFrame(), "tenure": 0.0, "retention": 0.0, "replacement_cost": 0.0, "onboarding_cost": 0.0, "risk_sites": pd.DataFrame()}

    leavers = employees[employees["termination_date"].notna()].copy()
    leavers["termination_date"] = pd.to_datetime(leavers["termination_date"], errors="coerce")
    leavers["month"] = leavers["termination_date"].dt.to_period("M").dt.to_timestamp()
    trend = leavers.groupby("month", as_index=False).size().rename(columns={"size": "leavers"})
    by_site = leavers.groupby("site", as_index=False).size().rename(columns={"size": "leavers"}).sort_values("leavers", ascending=False)
    by_department = leavers.groupby("department", as_index=False).size().rename(columns={"size": "leavers"}).sort_values("leavers", ascending=False)
    voluntary = max(0, int(len(leavers) * 0.68))
    involuntary = max(0, int(len(leavers) - voluntary))

    active = employees[employees["termination_date"].isna()].copy()
    active["hire_date"] = pd.to_datetime(active["hire_date"], errors="coerce")
    tenure_years = ((pd.Timestamp.today().normalize() - active["hire_date"]).dt.days / 365.25).clip(lower=0)
    avg_tenure = float(tenure_years.mean()) if not tenure_years.empty else 0.0
    retention = 100 - ((len(leavers[leavers["termination_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=365))]) / max(len(active), 1)) * 100)

    recruit = get_workforce_recruitment()
    replacement_cost = float(recruit.get("replacement_cost", pd.Series(dtype=float)).sum()) if not recruit.empty else 0.0
    onboarding_cost = float(recruit.get("onboarding_cost", pd.Series(dtype=float)).sum()) if not recruit.empty else 0.0

    risk_sites = by_site.head(4).copy()
    risk_sites["risk_level"] = np.where(risk_sites["leavers"] >= risk_sites["leavers"].quantile(0.75), "High", "Medium") if not risk_sites.empty else []
    return {
        "trend": trend,
        "by_site": by_site,
        "by_department": by_department,
        "voluntary": voluntary,
        "involuntary": involuntary,
        "tenure": avg_tenure,
        "retention": retention,
        "replacement_cost": replacement_cost,
        "onboarding_cost": onboarding_cost,
        "risk_sites": risk_sites,
    }


def get_labour_cost_analytics() -> dict:
    wf_daily = get_workforce_daily()
    orders = get_orders().copy()
    sites = get_sites()[["site_id", "site_name", "region"]].copy()
    if wf_daily.empty:
        return {"monthly": pd.DataFrame(), "site": pd.DataFrame(), "budget": pd.DataFrame(), "kpis": {}}

    d = wf_daily.copy()
    d["month"] = d["date"].dt.to_period("M").dt.to_timestamp()
    monthly = d.groupby("month", as_index=False).agg(labour_cost=("labour_cost", "sum"), overtime_cost=("overtime_hours", "sum"), agency_labour_cost=("agency_labour_cost", "sum"))
    monthly["budget"] = monthly["labour_cost"] * 0.96
    monthly["variance_pct"] = ((monthly["labour_cost"] - monthly["budget"]) / monthly["budget"].replace(0, np.nan) * 100).fillna(0)

    site = d.groupby("site_id", as_index=False).agg(labour_cost=("labour_cost", "sum"), overtime_hours=("overtime_hours", "sum"), agency_labour_cost=("agency_labour_cost", "sum"), headcount=("headcount", "mean")).merge(sites, on="site_id", how="left")
    site["site_name"] = site["site_name"].fillna(site["site_id"])

    orders_done = orders[orders["status"] == "Completed"] if "status" in orders.columns else orders
    order_count = max(1, len(orders_done))
    revenue = float(orders_done.get("revenue", pd.Series(dtype=float)).sum())
    total_cost = float(d["labour_cost"].sum())
    kpis = {
        "labour_per_order": total_cost / order_count,
        "labour_per_revenue": (total_cost / max(revenue, 1)) * 100,
        "revenue_per_employee": revenue / max(float(d["headcount"].mean()), 1),
    }
    return {"monthly": monthly, "site": site, "budget": monthly[["month", "labour_cost", "budget", "variance_pct"]], "kpis": kpis}


def get_productivity_analytics() -> dict:
    wf_daily = get_workforce_daily()
    employees = get_workforce_employees()
    orders = get_orders().copy()
    if wf_daily.empty:
        return {"monthly": pd.DataFrame(), "shift_output": pd.DataFrame(), "training": 0.0, "cross_skilled": 0.0, "utilisation": 0.0, "overtime": 0.0}

    orders_done = orders[orders["status"] == "Completed"] if "status" in orders.columns else orders
    orders_done["completion_date"] = pd.to_datetime(orders_done.get("completion_date"), errors="coerce")
    recent_orders = orders_done[orders_done["completion_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=90))]

    monthly = wf_daily.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").dt.to_timestamp()
    agg = monthly.groupby("month", as_index=False).agg(headcount=("headcount", "mean"), labour_cost=("labour_cost", "sum"), overtime=("overtime_hours", "mean"))
    rev = get_revenue_trend(120)
    rev["month"] = pd.to_datetime(rev["date"]).dt.to_period("M").dt.to_timestamp()
    revm = rev.groupby("month", as_index=False)["revenue"].sum()
    agg = agg.merge(revm, on="month", how="left")
    agg["revenue_per_employee"] = agg["revenue"] / agg["headcount"].replace(0, np.nan)
    agg["orders_per_employee"] = (len(recent_orders) / max(1, len(agg))) / agg["headcount"].replace(0, np.nan)

    active = employees[employees["termination_date"].isna()] if not employees.empty else employees
    shift_output = active.groupby("shift_pattern", as_index=False).agg(
        employees=("employee_id", "count"),
        overtime_hours=("overtime_hours", "mean"),
        performance=("performance_rating", "mean"),
    ) if not active.empty else pd.DataFrame(columns=["shift_pattern", "employees", "overtime_hours", "performance"])
    shift_output["output_index"] = (shift_output["performance"] * 22) + (shift_output["employees"] * 0.9) - (shift_output["overtime_hours"] * 1.7) if not shift_output.empty else 0

    training = float((active["training_status"] == "Compliant").mean() * 100) if not active.empty else 0.0
    cross_skilled = float(active.get("cross_skilled", pd.Series(dtype=bool)).mean() * 100) if not active.empty else 0.0
    util = float((get_daily_metrics().get("utilisation", pd.Series(dtype=float)).mean()))
    overtime = float(wf_daily["overtime_hours"].mean())

    return {
        "monthly": agg,
        "shift_output": shift_output,
        "training": training,
        "cross_skilled": cross_skilled,
        "utilisation": util,
        "overtime": overtime,
    }


def get_recruitment_analytics() -> dict:
    rec = get_workforce_recruitment()
    if rec.empty:
        return {"open_vacancies": 0, "applications": 0, "interviews": 0, "offers": 0, "acceptance": 0.0, "time_to_hire": 0.0, "time_to_fill": 0.0, "by_site": pd.DataFrame(), "critical": pd.DataFrame(), "pipeline": pd.DataFrame()}

    open_vacancies = int((rec["status"] == "Open").sum())
    applications = int(rec["applications"].sum())
    interviews = int(rec["interviews"].sum())
    offers = int(rec["offers"].sum())
    accepted = int(rec["accepted_offers"].sum())
    acceptance = (accepted / max(offers, 1)) * 100
    tth = float(rec["time_to_hire_days"].mean())
    ttf = float(rec["time_to_fill_days"].dropna().mean()) if rec["time_to_fill_days"].notna().any() else 0.0
    by_site = rec.groupby("site", as_index=False).agg(vacancies=("vacancy_id", "count"), open_vacancies=("status", lambda s: int((s == "Open").sum()))).sort_values("open_vacancies", ascending=False)
    critical = rec[rec["critical_skill"]].groupby(["site", "role"], as_index=False).size().rename(columns={"size": "vacancies"}).sort_values("vacancies", ascending=False)
    pipeline = pd.DataFrame(
        {
            "stage": ["Applications", "Interviews", "Offers", "Accepted"],
            "count": [applications, interviews, offers, accepted],
        }
    )
    return {
        "open_vacancies": open_vacancies,
        "applications": applications,
        "interviews": interviews,
        "offers": offers,
        "acceptance": acceptance,
        "time_to_hire": tth,
        "time_to_fill": ttf,
        "by_site": by_site,
        "critical": critical,
        "pipeline": pipeline,
    }


def get_safety_analytics() -> dict:
    safety = get_workforce_safety()
    employees = get_workforce_employees()
    if safety.empty:
        return {"days_since_lti": 0, "recordable": 0, "near_misses": 0, "observations": 0, "training": 0.0, "trend": pd.DataFrame(), "risk_site": pd.DataFrame()}

    safety["event_date"] = pd.to_datetime(safety["event_date"], errors="coerce")
    recent = safety[safety["event_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=90))]
    lti_dates = safety[safety["event_type"] == "LTI"]["event_date"].sort_values()
    days_since_lti = int((pd.Timestamp.today().normalize() - lti_dates.iloc[-1]).days) if not lti_dates.empty else 365
    recordable = int((recent["event_type"] == "Recordable").sum())
    near_misses = int((recent["event_type"] == "Near Miss").sum())
    observations = int((recent["event_type"] == "Observation").sum())
    training = float((employees.get("safety_training", pd.Series(dtype=str)) == "Completed").mean() * 100) if not employees.empty else 0.0

    recent["month"] = recent["event_date"].dt.to_period("M").dt.to_timestamp()
    trend = recent.groupby(["month", "event_type"], as_index=False).size().rename(columns={"size": "count"})
    risk_site = recent.groupby(["site", "risk_rating"], as_index=False).size().rename(columns={"size": "events"})
    return {
        "days_since_lti": days_since_lti,
        "recordable": recordable,
        "near_misses": near_misses,
        "observations": observations,
        "training": training,
        "trend": trend,
        "risk_site": risk_site,
    }


def get_site_workforce_comparison() -> pd.DataFrame:
    sites = get_sites()[["site_id", "site_name", "region"]].copy()
    wf_daily = _window(get_workforce_daily(), 30)
    employees = get_workforce_employees()
    orders = get_orders().copy()
    safety = _window(get_workforce_daily(), 30)

    if wf_daily.empty:
        return pd.DataFrame()

    agg = wf_daily.groupby("site_id", as_index=False).agg(
        headcount=("headcount", "mean"),
        absence_pct=("absence_rate", "mean"),
        labour_cost=("labour_cost", "sum"),
        overtime=("overtime_hours", "mean"),
        safety_rating=("recordable_incidents", "sum"),
        workforce_health_score=("absence_rate", lambda s: max(0.0, 100 - float(s.mean() * 8))),
    )

    leavers = employees[employees["termination_date"].notna()].copy() if not employees.empty else pd.DataFrame()
    if not leavers.empty:
        leavers["termination_date"] = pd.to_datetime(leavers["termination_date"], errors="coerce")
        leavers = leavers[leavers["termination_date"] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=90))]
        turn = leavers.groupby("site_id", as_index=False).size().rename(columns={"size": "leavers"})
        agg = agg.merge(turn, on="site_id", how="left")
    else:
        agg["leavers"] = 0

    agg["turnover_pct"] = (agg["leavers"] / agg["headcount"].replace(0, np.nan) * 100).fillna(0)

    orders_done = orders[orders["status"] == "Completed"] if "status" in orders.columns else orders
    rev = orders_done.groupby("site_id", as_index=False)["revenue"].sum() if not orders_done.empty else pd.DataFrame(columns=["site_id", "revenue"])
    agg = agg.merge(rev, on="site_id", how="left")
    agg["revenue"] = agg["revenue"].fillna(0)
    agg["revenue_per_employee"] = agg["revenue"] / agg["headcount"].replace(0, np.nan)
    agg["overall_site_score"] = (
        (100 - agg["absence_pct"].clip(upper=12) * 6)
        + (100 - agg["turnover_pct"].clip(upper=20) * 3)
        + (agg["workforce_health_score"])
        + (100 - agg["safety_rating"].clip(upper=10) * 6)
    ) / 4

    out = agg.merge(sites, on="site_id", how="left")
    out["site"] = out["site_name"].fillna(out["site_id"])
    return out[
        [
            "site",
            "headcount",
            "absence_pct",
            "turnover_pct",
            "labour_cost",
            "revenue_per_employee",
            "overtime",
            "safety_rating",
            "workforce_health_score",
            "overall_site_score",
            "region",
        ]
    ].sort_values("overall_site_score", ascending=False)


def get_executive_insights() -> list[dict]:
    comparison = get_site_workforce_comparison()
    labour = get_labour_cost_analytics()
    turnover = get_turnover_analytics()
    absence = get_absence_analytics()
    productivity = get_productivity_analytics()

    insights = []
    if not comparison.empty:
        risk_site = comparison.sort_values("absence_pct", ascending=False).iloc[0]
        if float(risk_site["absence_pct"]) > 4:
            insights.append(
                {
                    "message": f"Absence at {risk_site['site']} exceeds target by {float(risk_site['absence_pct']) - 3.2:.1f}%.",
                    "severity": "warning",
                    "impact": "Potential overtime and schedule pressure on production lines.",
                    "action": "Deploy targeted return-to-work and shift balancing plan.",
                }
            )

    budget = labour.get("budget", pd.DataFrame())
    if not budget.empty:
        latest = budget.sort_values("month").iloc[-1]
        if float(latest["variance_pct"]) > 0:
            insights.append(
                {
                    "message": f"Overtime and labour spend increased {float(latest['variance_pct']):.1f}% above budget this month.",
                    "severity": "critical" if float(latest["variance_pct"]) > 8 else "warning",
                    "impact": "Margin erosion risk on lower-yield orders.",
                    "action": "Rebalance shift cover and accelerate vacancy closure at high-pressure sites.",
                }
            )

    if turnover.get("retention", 100) > 96:
        insights.append(
            {
                "message": "Retention remains above target across most sites.",
                "severity": "success",
                "impact": "Supports continuity in throughput and quality consistency.",
                "action": "Sustain manager coaching and progression pathways in high-performing teams.",
            }
        )

    if productivity.get("training", 0) >= 95:
        insights.append(
            {
                "message": "Training compliance exceeds target in the active workforce.",
                "severity": "success",
                "impact": "Improves quality and safety resilience under peak load.",
                "action": "Continue compliance cadence and close remaining overdue modules.",
            }
        )

    if absence.get("kpi", {}).get("absence_rate", 0) > 3.2:
        insights.append(
            {
                "message": "Absence trend is climbing month-on-month and may affect on-time delivery.",
                "severity": "warning",
                "impact": "Higher temporary labour and overtime costs likely over next cycle.",
                "action": "Trigger site-level absence deep dives in highest-risk departments.",
            }
        )

    return insights[:6]


def _rolling_projection(series: pd.Series, horizon_days: int = 30) -> tuple[float, float]:
    if series.empty:
        return 0.0, 0.0
    vals = series.dropna().astype(float).values
    if len(vals) < 3:
        return float(vals[-1]), 65.0
    short = float(np.mean(vals[-7:])) if len(vals) >= 7 else float(np.mean(vals))
    long = float(np.mean(vals[-30:])) if len(vals) >= 30 else float(np.mean(vals))
    drift = (short - long) * (horizon_days / 30)
    forecast = max(0.0, short + drift)
    volatility = float(np.std(vals[-30:])) if len(vals) >= 30 else float(np.std(vals))
    confidence = max(58.0, min(96.0, 94.0 - (volatility * 2.2)))
    return forecast, confidence


def get_executive_forecast() -> dict:
    wf = get_workforce_daily().copy()
    if "date" in wf.columns:
        wf = wf.sort_values("date")
    daily = get_daily_metrics().copy()
    if "date" in daily.columns:
        daily["date"] = pd.to_datetime(daily["date"], errors="coerce")
        daily = daily.sort_values("date")
    else:
        daily = pd.DataFrame(columns=["date", "utilisation", "on_time_delivery_pct"])

    abs_fc, abs_conf = _rolling_projection(wf.groupby("date")['absence_rate'].mean() if not wf.empty else pd.Series(dtype=float), 30)
    overtime_fc, over_conf = _rolling_projection(wf.groupby("date")['overtime_hours'].mean() if not wf.empty else pd.Series(dtype=float), 30)
    labour_fc, labour_conf = _rolling_projection(wf.groupby("date")['labour_cost'].sum() if not wf.empty else pd.Series(dtype=float), 30)
    util_fc, util_conf = _rolling_projection(daily.groupby("date")['utilisation'].mean() if not daily.empty else pd.Series(dtype=float), 14)
    delivery_fc, del_conf = _rolling_projection(daily.groupby("date")['on_time_delivery_pct'].mean() if not daily.empty else pd.Series(dtype=float), 30)
    backlog_fc, back_conf = _rolling_projection(get_orders()["status"].eq("In Progress").astype(float) if "status" in get_orders().columns else pd.Series(dtype=float), 14)

    risk = (
        min(35, abs_fc * 4.2)
        + min(20, max(0, overtime_fc - 9) * 2.2)
        + min(15, max(0, (100 - delivery_fc) * 0.8))
        + min(12, max(0, util_fc - 85) * 1.4)
        + min(18, max(0, backlog_fc * 7.5))
    )
    risk_score = int(max(5, min(96, round(risk))))

    outlook = "Stable"
    if risk_score >= 65:
        outlook = "At Risk"
    elif risk_score >= 40:
        outlook = "Watch"

    forecast_conf = int(round(np.mean([abs_conf, over_conf, labour_conf, util_conf, del_conf, back_conf])))

    predictive_cards = [
        {
            "title": "Absence Forecast",
            "predicted_value": f"{abs_fc:.1f}%",
            "confidence": int(abs_conf),
            "horizon": "Next 30 days",
            "impact": "Potential increase in cover costs and overtime.",
            "risk": "Amber" if abs_fc > 3.2 else "Green",
            "action": "Prioritise attendance interventions at highest-risk sites.",
            "spark": [max(0.5, abs_fc - 0.9), abs_fc - 0.5, abs_fc - 0.2, abs_fc],
            "icon": "monitor_heart",
        },
        {
            "title": "Capacity Pressure",
            "predicted_value": f"{util_fc:.1f}% utilisation",
            "confidence": int(util_conf),
            "horizon": "Next 14 days",
            "impact": "Risk of queue build-up at high-load furnaces.",
            "risk": "Red" if util_fc > 90 else "Amber" if util_fc > 84 else "Green",
            "action": "Shift non-urgent jobs across regional network.",
            "spark": [util_fc - 3, util_fc - 2, util_fc - 1, util_fc],
            "icon": "precision_manufacturing",
        },
        {
            "title": "Overtime Spend",
            "predicted_value": f"{overtime_fc:.1f} hrs/day",
            "confidence": int(over_conf),
            "horizon": "Next 30 days",
            "impact": "Erodes gross margin if sustained.",
            "risk": "Red" if overtime_fc > 12 else "Amber" if overtime_fc > 9 else "Green",
            "action": "Accelerate recruitment for critical shifts and rebalance rosters.",
            "spark": [overtime_fc - 1.2, overtime_fc - 0.6, overtime_fc - 0.2, overtime_fc],
            "icon": "schedule",
        },
        {
            "title": "Labour Cost Trajectory",
            "predicted_value": f"£{labour_fc / 1000:.0f}k",
            "confidence": int(labour_conf),
            "horizon": "Next month",
            "impact": "Budget overrun risk if unmitigated.",
            "risk": "Red" if labour_fc > 430000 else "Amber" if labour_fc > 390000 else "Green",
            "action": "Apply temporary cost controls on agency allocation.",
            "spark": [labour_fc * 0.92, labour_fc * 0.96, labour_fc * 0.99, labour_fc],
            "icon": "paid",
        },
        {
            "title": "Delivery Performance",
            "predicted_value": f"{delivery_fc:.1f}%",
            "confidence": int(del_conf),
            "horizon": "Next 30 days",
            "impact": "Service-level risk for strategic accounts.",
            "risk": "Amber" if delivery_fc < 95 else "Green",
            "action": "Protect expedited lanes for constrained sites.",
            "spark": [delivery_fc + 1.5, delivery_fc + 0.7, delivery_fc + 0.2, delivery_fc],
            "icon": "local_shipping",
        },
        {
            "title": "Maintenance Backlog Signal",
            "predicted_value": f"{backlog_fc:.1f} backlog index",
            "confidence": int(back_conf),
            "horizon": "Next 2 weeks",
            "impact": "Potential throughput bottleneck if unresolved.",
            "risk": "Amber" if backlog_fc > 1.8 else "Green",
            "action": "Bring forward planned interventions for high-risk assets.",
            "spark": [max(0, backlog_fc - 0.7), max(0, backlog_fc - 0.4), max(0, backlog_fc - 0.1), backlog_fc],
            "icon": "build",
        },
    ]

    outlook_text = (
        "Based on operational and workforce trends, performance is expected to remain "
        f"{outlook.lower()} over the next 30 days. "
        f"Forecast absence sits at {abs_fc:.1f}% and overtime at {overtime_fc:.1f} hours/day, "
        "which may increase labour costs in constrained sites. "
        f"Delivery is projected at {delivery_fc:.1f}%, with targeted interventions recommended "
        "for capacity and maintenance hotspots."
    )

    risk_matrix = pd.DataFrame(
        [
            {"Category": "People", "Current Risk": "Medium" if abs_fc > 3.2 else "Low", "Trend": "Rising" if abs_fc > 3.2 else "Stable", "Forecast Direction": "Up", "Colour": "Amber" if abs_fc > 3.2 else "Green"},
            {"Category": "Operations", "Current Risk": "High" if util_fc > 90 else "Medium", "Trend": "Rising" if util_fc > 88 else "Stable", "Forecast Direction": "Up", "Colour": "Red" if util_fc > 90 else "Amber"},
            {"Category": "Quality", "Current Risk": "Medium" if delivery_fc < 95 else "Low", "Trend": "Stable", "Forecast Direction": "Flat", "Colour": "Amber" if delivery_fc < 95 else "Green"},
            {"Category": "Maintenance", "Current Risk": "Medium" if backlog_fc > 1.8 else "Low", "Trend": "Rising" if backlog_fc > 1.8 else "Stable", "Forecast Direction": "Up", "Colour": "Amber" if backlog_fc > 1.8 else "Green"},
            {"Category": "Delivery", "Current Risk": "Medium" if delivery_fc < 95 else "Low", "Trend": "Declining" if delivery_fc < 95 else "Stable", "Forecast Direction": "Down", "Colour": "Amber" if delivery_fc < 95 else "Green"},
            {"Category": "Finance", "Current Risk": "High" if labour_fc > 430000 else "Medium", "Trend": "Rising", "Forecast Direction": "Up", "Colour": "Red" if labour_fc > 430000 else "Amber"},
            {"Category": "Supply Chain", "Current Risk": "Medium", "Trend": "Stable", "Forecast Direction": "Flat", "Colour": "Amber"},
        ]
    )

    return {
        "outlook": outlook,
        "risk_score": risk_score,
        "confidence": forecast_conf,
        "horizon": "Next 30 Days",
        "predictive_cards": predictive_cards,
        "outlook_summary": outlook_text,
        "risk_matrix": risk_matrix,
    }
