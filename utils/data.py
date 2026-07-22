"""
Data utilities and caching for Bodycote Command Centre
"""

import streamlit as st
from data.generate_demo_data import generate_all_data
import pandas as pd
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
