"""Quality analytics page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import charts
from utils.data import get_complaints, get_daily_metrics, get_first_pass_yield, get_orders, get_site_performance
from utils.helpers import COLORS, create_metric_card, format_number, format_percentage


def _quality_metrics(orders: pd.DataFrame) -> tuple[float, float, float, int]:
    completed = orders[orders["status"] == "Completed"] if "status" in orders.columns else orders
    if completed.empty:
        return 0.0, 0.0, 0.0, 0

    total = len(completed)
    passes = len(completed[completed["quality_result"] == "Pass"]) if "quality_result" in completed.columns else 0
    rework = len(completed[completed["quality_result"] == "Rework"]) if "quality_result" in completed.columns else 0
    reject = len(completed[completed["quality_result"] == "Reject"]) if "quality_result" in completed.columns else 0

    fpy = (passes / total) * 100 if total else 0.0
    rework_rate = (rework / total) * 100 if total else 0.0
    reject_rate = (reject / total) * 100 if total else 0.0
    return fpy, rework_rate, reject_rate, total


def _complaints_last_30_days(complaints: pd.DataFrame) -> int:
    if complaints.empty or "date_raised" not in complaints.columns:
        return 0
    c = complaints.copy()
    c["date_raised"] = pd.to_datetime(c["date_raised"], errors="coerce")
    cutoff = pd.Timestamp.today() - pd.Timedelta(days=30)
    return int((c["date_raised"] >= cutoff).sum())


def _render_quality_breakdown(orders: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Quality Outcome Mix</div>", unsafe_allow_html=True)
    if "quality_result" not in orders.columns:
        st.info("Quality result data is unavailable.")
        return

    completed = orders[orders["status"] == "Completed"] if "status" in orders.columns else orders
    mix = completed["quality_result"].value_counts().reset_index()
    mix.columns = ["quality_result", "count"]
    if mix.empty:
        st.info("No completed quality outcomes available.")
        return

    fig = px.pie(
        mix,
        names="quality_result",
        values="count",
        hole=0.55,
        color="quality_result",
        color_discrete_map={"Pass": "#16A34A", "Rework": "#F59E0B", "Reject": "#DC2626"},
    )
    fig.update_layout(title=dict(text="Completed Orders by Quality Result", x=0))
    st.plotly_chart(charts.apply_template(fig), use_container_width=True)


def _render_quality_by_site(site_perf: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>First Pass Yield by Site</div>", unsafe_allow_html=True)
    if site_perf.empty:
        st.info("Site performance data unavailable.")
        return
    if "first_pass_yield" not in site_perf.columns:
        st.info("First pass yield data unavailable in site performance.")
        return

    x_col = "site_name" if "site_name" in site_perf.columns else "site_id"
    fig = px.bar(
        site_perf.sort_values("first_pass_yield", ascending=False),
        x=x_col,
        y="first_pass_yield",
        color="first_pass_yield",
        color_continuous_scale=[[0, "#DC2626"], [0.5, "#F59E0B"], [1, "#16A34A"]],
    )
    fig.add_hline(y=95, line_dash="dash", line_color=COLORS["warning"])
    fig.update_layout(title=dict(text="Site Quality Performance", x=0), yaxis_title="First Pass Yield %")
    st.plotly_chart(charts.apply_template(fig), use_container_width=True)


def _render_complaints(complaints: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Complaints Overview</div>", unsafe_allow_html=True)
    if complaints.empty:
        st.info("No complaint records available.")
        return

    c = complaints.copy()
    if "date_raised" in c.columns:
        c["date_raised"] = pd.to_datetime(c["date_raised"], errors="coerce")

    col1, col2 = st.columns(2)
    with col1:
        if "severity" in c.columns:
            sev = c["severity"].value_counts().reset_index()
            sev.columns = ["severity", "count"]
            fig = px.bar(sev, x="severity", y="count", color="severity")
            fig.update_layout(title=dict(text="Complaints by Severity", x=0), showlegend=False)
            st.plotly_chart(charts.apply_template(fig), use_container_width=True)
        else:
            st.info("Severity field unavailable.")

    with col2:
        if "status" in c.columns:
            status = c["status"].value_counts().reset_index()
            status.columns = ["status", "count"]
            fig = px.bar(status, x="status", y="count", color="status")
            fig.update_layout(title=dict(text="Complaint Status", x=0), showlegend=False)
            st.plotly_chart(charts.apply_template(fig), use_container_width=True)
        else:
            st.info("Complaint status field unavailable.")


def render_page() -> None:
    st.markdown("<div class='page-title'>Quality Intelligence</div>", unsafe_allow_html=True)

    orders = get_orders().copy()
    complaints = get_complaints().copy()
    daily = get_daily_metrics().copy()
    site_perf = get_site_performance().copy()

    if "region" in site_perf.columns:
        region_options = ["All Regions"] + sorted(site_perf["region"].dropna().astype(str).unique().tolist())
        selected_region = st.selectbox("Region", options=region_options)
        if selected_region != "All Regions":
            site_perf = site_perf[site_perf["region"] == selected_region]
            if "site_id" in site_perf.columns and "site_id" in orders.columns:
                orders = orders[orders["site_id"].isin(site_perf["site_id"].tolist())]

    fpy, rework_rate, reject_rate, completed_count = _quality_metrics(orders)
    complaints_30 = _complaints_last_30_days(complaints)

    kpi = st.columns(4)
    with kpi[0]:
        create_metric_card("First Pass Yield", format_percentage(fpy), delta=f"{fpy - 95:+.1f}%", target="Target: 95%", icon="verified", border_color=COLORS["success"])
    with kpi[1]:
        create_metric_card("Rework Rate", format_percentage(rework_rate), delta="-0.7%", target="Target: < 3%", icon="build", border_color=COLORS["warning"])
    with kpi[2]:
        create_metric_card("Reject Rate", format_percentage(reject_rate), delta="-0.4%", target="Target: < 1%", icon="report", border_color=COLORS["critical"])
    with kpi[3]:
        create_metric_card("Complaints (30d)", format_number(complaints_30), delta="-2", target="Target: 0", icon="feedback")

    chart_row = st.columns(2)
    with chart_row[0]:
        st.plotly_chart(charts.quality_trend_chart(daily), use_container_width=True)
    with chart_row[1]:
        _render_quality_breakdown(orders)

    _render_quality_by_site(site_perf)
    _render_complaints(complaints)

    st.markdown("<div class='section-title'>Quality Records</div>", unsafe_allow_html=True)
    display_cols = [
        c
        for c in [
            "order_id",
            "site_id",
            "process",
            "material",
            "status",
            "quality_result",
            "priority",
            "received_date",
            "completion_date",
        ]
        if c in orders.columns
    ]
    quality_records = orders.copy()
    if "quality_result" in quality_records.columns:
        quality_records = quality_records[quality_records["quality_result"].isin(["Pass", "Rework", "Reject"])]
    st.dataframe(quality_records[display_cols].head(400), use_container_width=True, height=420)


def render() -> None:
    render_page()


def main() -> None:
    render_page()
