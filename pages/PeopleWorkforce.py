"""People and workforce executive dashboard page."""

from __future__ import annotations

from typing import Iterable

import pandas as pd
import streamlit as st

from utils import charts
from utils.data import (
    get_absence_analytics,
    get_executive_insights,
    get_labour_cost_analytics,
    get_productivity_analytics,
    get_recruitment_analytics,
    get_safety_analytics,
    get_site_workforce_comparison,
    get_turnover_analytics,
    get_workforce_kpi_pack,
)
from utils.helpers import COLORS, format_currency, format_number, format_percentage


def _sparkline(series: Iterable[float], color: str) -> str:
    values = [float(v) for v in series] if series else [1, 2, 3, 3, 4]
    low = min(values)
    high = max(values)
    spread = (high - low) if high != low else 1
    pts = []
    for i, value in enumerate(values):
        x = (i / max(1, len(values) - 1)) * 100
        y = 20 - ((value - low) / spread) * 16
        pts.append(f"{x:.1f},{y:.1f}")
    points = " ".join(pts)
    return (
        "<svg class='sparkline' viewBox='0 0 100 24' preserveAspectRatio='none'>"
        f"<polyline fill='none' stroke='{color}' stroke-width='2.2' points='{points}' /></svg>"
    )


def _status_color(status: str) -> str:
    s = (status or "").lower()
    if s == "success":
        return COLORS["success"]
    if s == "warning":
        return COLORS["warning"]
    return COLORS["critical"]


def _format_metric_value(name: str, value: float, unit: str) -> str:
    if "Cost" in name or "Revenue" in name:
        return format_currency(value)
    if "Rate" in name or unit == "%" or "Compliance" in name or "Turnover" in name or "Retention" in name:
        return format_percentage(value)
    if "Time to Fill" in name:
        return f"{value:.1f} days"
    if "Hours" in name:
        return f"{value:.1f} h"
    if "Score" in name:
        return f"{value:.1f}"
    return format_number(value)


def _render_exec_kpi_cards() -> None:
    kpis = get_workforce_kpi_pack()
    if not kpis:
        st.info("No workforce KPI data available.")
        return

    chunks = [kpis[i : i + 4] for i in range(0, len(kpis), 4)]
    for chunk in chunks:
        cols = st.columns(4)
        for idx, item in enumerate(chunk):
            with cols[idx]:
                color = _status_color(item["status"])
                trend_arrow = "↑" if item["trend"] == "up" else "↓"
                cur = _format_metric_value(item["name"], float(item["current"]), item.get("unit", ""))
                prev = _format_metric_value(item["name"], float(item["previous"]), item.get("unit", ""))
                tgt = _format_metric_value(item["name"], float(item["target"]), item.get("unit", ""))
                delta = f"{item['change_pct']:+.1f}%"
                tooltip = (
                    f"Current: {cur} | Previous: {prev} | Target: {tgt} | "
                    f"Change: {delta}"
                )
                st.markdown(
                    f"""
                    <div class='metric-card fade-in' title='{tooltip}' style='border-left-color:{color}'>
                      <div class='metric-top'>
                        <div class='metric-title'>{item['name']}</div>
                      </div>
                      <div class='metric-value'>{cur}</div>
                      <div class='metric-row'>
                        <div class='metric-delta' style='color:{color}'>{trend_arrow} {delta}</div>
                        <div class='target-pill'>Target: {tgt}</div>
                      </div>
                      <div style='font-size:11px;color:#64748B;margin-top:6px'>Previous: {prev}</div>
                      {_sparkline(item['spark'], color)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _render_absence_tab() -> None:
    data = get_absence_analytics()
    st.markdown("<div class='section-title'>Absence Analytics</div>", unsafe_allow_html=True)

    top = st.columns(3)
    with top[0]:
        st.plotly_chart(charts.workforce_trend_chart(data["trend"], "month", "lost_days", "Monthly Lost Working Days"), use_container_width=True)
    with top[1]:
        st.plotly_chart(charts.workforce_bar_chart(data["by_site"], "site", "absence_rate", "Absence by Site"), use_container_width=True)
    with top[2]:
        st.plotly_chart(charts.workforce_bar_chart(data["by_department"], "department", "lost_days", "Absence by Department"), use_container_width=True)

    mid = st.columns(3)
    with mid[0]:
        st.plotly_chart(charts.workforce_bar_chart(data["by_shift"], "shift_pattern", "lost_days", "Absence by Shift"), use_container_width=True)
    with mid[1]:
        st.plotly_chart(charts.workforce_pie_chart(data["types"], "absence_type", "lost_days", "Short-term vs Long-term"), use_container_width=True)
    with mid[2]:
        st.plotly_chart(charts.workforce_bar_chart(data["reasons"], "absence_reason", "lost_days", "Top Absence Reasons"), use_container_width=True)

    low = st.columns(3)
    with low[0]:
        st.plotly_chart(charts.workforce_histogram(data["bradford"], "bradford_factor", "Bradford Factor Distribution"), use_container_width=True)
    with low[1]:
        st.plotly_chart(charts.workforce_bar_chart(data["cost_site"], "site", "estimated_cost", "Absence Cost per Site"), use_container_width=True)
    with low[2]:
        alert_sites = data["threshold_sites"]
        st.markdown("<div class='surface-card'><div class='section-title' style='font-size:16px'>Sites Above Absence Threshold</div>", unsafe_allow_html=True)
        if alert_sites.empty:
            st.markdown("<div style='color:#64748B'>All sites are within target absence bands.</div></div>", unsafe_allow_html=True)
        else:
            for _, row in alert_sites.iterrows():
                st.markdown(
                    f"<div style='margin-bottom:8px'><span class='status-pill status-delayed'>{row['site_name']}</span> "
                    f"<span style='font-weight:700;color:#B91C1C'>{row['absence_rate']:.2f}%</span></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)


def _render_turnover_tab() -> None:
    data = get_turnover_analytics()
    st.markdown("<div class='section-title'>Staff Turnover</div>", unsafe_allow_html=True)

    row1 = st.columns(3)
    with row1[0]:
        st.plotly_chart(charts.workforce_trend_chart(data["trend"], "month", "leavers", "Monthly Turnover Trend", color=COLORS["warning"]), use_container_width=True)
    with row1[1]:
        st.plotly_chart(charts.workforce_bar_chart(data["by_site"], "site", "leavers", "Turnover by Site"), use_container_width=True)
    with row1[2]:
        st.plotly_chart(charts.workforce_bar_chart(data["by_department"], "department", "leavers", "Turnover by Department"), use_container_width=True)

    row2 = st.columns(4)
    row2[0].metric("Voluntary Resignations", format_number(data["voluntary"]))
    row2[1].metric("Involuntary Leavers", format_number(data["involuntary"]))
    row2[2].metric("Average Tenure", f"{data['tenure']:.1f} yrs")
    row2[3].metric("Retention Rate", format_percentage(data["retention"]))

    row3 = st.columns(2)
    row3[0].metric("Recruitment Replacement Cost", format_currency(data["replacement_cost"]))
    row3[1].metric("Estimated Onboarding Cost", format_currency(data["onboarding_cost"]))

    st.markdown("<div class='surface-card'><div class='section-title' style='font-size:16px'>High-Risk Sites</div>", unsafe_allow_html=True)
    risk_sites = data["risk_sites"]
    if risk_sites.empty:
        st.markdown("<div style='color:#64748B'>No current high-risk turnover sites.</div></div>", unsafe_allow_html=True)
    else:
        for _, row in risk_sites.iterrows():
            css = "status-critical" if row["risk_level"] == "High" else "status-maintenance"
            st.markdown(
                f"<div style='margin-bottom:8px'><span class='status-pill {css}'>{row['site']}</span> "
                f"<span style='color:#334155'>Leavers: {int(row['leavers'])}</span></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def _render_labour_tab() -> None:
    data = get_labour_cost_analytics()
    st.markdown("<div class='section-title'>Labour Cost Analytics</div>", unsafe_allow_html=True)

    top = st.columns(2)
    with top[0]:
        st.plotly_chart(charts.workforce_trend_chart(data["monthly"], "month", "labour_cost", "Monthly Labour Costs"), use_container_width=True)
    with top[1]:
        st.plotly_chart(charts.budget_vs_actual_chart(data["budget"]), use_container_width=True)

    mid = st.columns(3)
    with mid[0]:
        st.plotly_chart(charts.workforce_bar_chart(data["site"], "site_name", "labour_cost", "Labour Cost by Site"), use_container_width=True)
    with mid[1]:
        st.plotly_chart(charts.workforce_bar_chart(data["site"], "site_name", "overtime_hours", "Overtime Cost Pressure"), use_container_width=True)
    with mid[2]:
        st.plotly_chart(charts.workforce_bar_chart(data["site"], "site_name", "agency_labour_cost", "Agency Labour Cost"), use_container_width=True)

    bot = st.columns(3)
    bot[0].metric("Labour Cost per Production Order", format_currency(data["kpis"]["labour_per_order"]))
    bot[1].metric("Labour Cost per Revenue Generated", f"{data['kpis']['labour_per_revenue']:.2f}%")
    bot[2].metric("Revenue per Employee", format_currency(data["kpis"]["revenue_per_employee"]))


def _render_productivity_tab() -> None:
    data = get_productivity_analytics()
    st.markdown("<div class='section-title'>Workforce Productivity</div>", unsafe_allow_html=True)

    top = st.columns(2)
    with top[0]:
        st.plotly_chart(charts.workforce_trend_chart(data["monthly"], "month", "revenue_per_employee", "Revenue per Employee", color=COLORS["success"]), use_container_width=True)
    with top[1]:
        st.plotly_chart(charts.workforce_trend_chart(data["monthly"], "month", "orders_per_employee", "Orders per Employee", color=COLORS["accent"]), use_container_width=True)

    mid = st.columns(2)
    with mid[0]:
        st.plotly_chart(charts.workforce_bar_chart(data["shift_output"], "shift_pattern", "output_index", "Output by Shift"), use_container_width=True)
    with mid[1]:
        st.plotly_chart(charts.workforce_bar_chart(data["shift_output"], "shift_pattern", "overtime_hours", "Average Overtime by Shift"), use_container_width=True)

    bot = st.columns(4)
    bot[0].metric("Training Compliance", format_percentage(data["training"]))
    bot[1].metric("Cross-skilled Workforce", format_percentage(data["cross_skilled"]))
    bot[2].metric("Employee Utilisation", format_percentage(data["utilisation"]))
    bot[3].metric("Average Overtime", f"{data['overtime']:.1f} h")


def _render_recruitment_tab() -> None:
    data = get_recruitment_analytics()
    st.markdown("<div class='section-title'>Recruitment</div>", unsafe_allow_html=True)

    k = st.columns(6)
    k[0].metric("Open Vacancies", format_number(data["open_vacancies"]))
    k[1].metric("Applications", format_number(data["applications"]))
    k[2].metric("Interviews", format_number(data["interviews"]))
    k[3].metric("Offer Acceptance", format_percentage(data["acceptance"]))
    k[4].metric("Time to Hire", f"{data['time_to_hire']:.1f} days")
    k[5].metric("Time to Fill", f"{data['time_to_fill']:.1f} days")

    row = st.columns(3)
    with row[0]:
        st.plotly_chart(charts.workforce_bar_chart(data["by_site"], "site", "open_vacancies", "Vacancies by Site"), use_container_width=True)
    with row[1]:
        st.plotly_chart(charts.workforce_bar_chart(data["critical"], "site", "vacancies", "Critical Skill Shortages", color="role"), use_container_width=True)
    with row[2]:
        st.plotly_chart(charts.workforce_pie_chart(data["pipeline"], "stage", "count", "Interview Pipeline"), use_container_width=True)


def _render_safety_tab() -> None:
    data = get_safety_analytics()
    st.markdown("<div class='section-title'>Health & Safety</div>", unsafe_allow_html=True)

    k = st.columns(5)
    k[0].metric("Days Since Last LTI", format_number(data["days_since_lti"]))
    k[1].metric("Recordable Incidents", format_number(data["recordable"]))
    k[2].metric("Near Misses", format_number(data["near_misses"]))
    k[3].metric("Safety Observations", format_number(data["observations"]))
    k[4].metric("Training Compliance", format_percentage(data["training"]))

    row = st.columns(2)
    with row[0]:
        st.plotly_chart(charts.workforce_bar_chart(data["trend"], "month", "count", "Incident Trend", color="event_type"), use_container_width=True)
    with row[1]:
        pivot = data["risk_site"].pivot_table(index="site", columns="risk_rating", values="events", aggfunc="sum", fill_value=0).reset_index() if not data["risk_site"].empty else pd.DataFrame()
        if pivot.empty:
            st.info("No site risk data available.")
        else:
            melted = pivot.melt(id_vars=["site"], var_name="risk_rating", value_name="events")
            st.plotly_chart(charts.workforce_bar_chart(melted, "site", "events", "Risk Rating by Site", color="risk_rating"), use_container_width=True)


def _render_site_comparison_tab() -> None:
    st.markdown("<div class='section-title'>Site Comparison</div>", unsafe_allow_html=True)
    df = get_site_workforce_comparison()
    if df.empty:
        st.info("No workforce site comparison data available.")
        return

    region_options = ["All"] + sorted(df["region"].dropna().unique().tolist())
    c1, c2 = st.columns([1, 1])
    region_filter = c1.selectbox("Region", region_options)
    sort_by = c2.selectbox("Sort By", ["overall_site_score", "absence_pct", "turnover_pct", "revenue_per_employee", "labour_cost"])

    filt = df.copy()
    if region_filter != "All":
        filt = filt[filt["region"] == region_filter]
    ascending = sort_by in {"absence_pct", "turnover_pct", "labour_cost"}
    filt = filt.sort_values(sort_by, ascending=ascending)

    filt["Safety Rating"] = filt["safety_rating"].apply(lambda x: "Green" if x <= 2 else "Amber" if x <= 5 else "Red")
    filt["Workforce Health Score"] = filt["workforce_health_score"].round(1)
    filt["Overall Site Score"] = filt["overall_site_score"].round(1)
    filt["Status"] = filt["Overall Site Score"].apply(lambda x: "● Strong" if x >= 80 else "● Watch" if x >= 65 else "● Risk")

    view = filt[
        [
            "site",
            "headcount",
            "absence_pct",
            "turnover_pct",
            "labour_cost",
            "revenue_per_employee",
            "overtime",
            "Safety Rating",
            "Workforce Health Score",
            "Overall Site Score",
            "Status",
        ]
    ].rename(
        columns={
            "site": "Site",
            "headcount": "Headcount",
            "absence_pct": "Absence %",
            "turnover_pct": "Turnover %",
            "labour_cost": "Labour Cost",
            "revenue_per_employee": "Revenue per Employee",
            "overtime": "Overtime",
        }
    )

    fmt = {
        "Headcount": "{:.0f}",
        "Absence %": "{:.2f}",
        "Turnover %": "{:.2f}",
        "Labour Cost": "£{:,.0f}",
        "Revenue per Employee": "£{:,.0f}",
        "Overtime": "{:.1f}",
        "Workforce Health Score": "{:.1f}",
        "Overall Site Score": "{:.1f}",
    }

    try:
        styled = (
            view.style
            .format(fmt)
            .background_gradient(subset=["Overall Site Score"], cmap="Greens")
            .background_gradient(subset=["Absence %", "Turnover %"], cmap="Reds")
        )
        st.dataframe(styled, use_container_width=True, height=420)
    except ImportError:
        # Streamlit Cloud images may miss optional styling deps; show a robust fallback table.
        fallback = view.copy()
        fallback["Score Band"] = fallback["Overall Site Score"].apply(
            lambda x: "Strong" if x >= 80 else "Watch" if x >= 65 else "Risk"
        )
        fallback["Absence Band"] = fallback["Absence %"].apply(
            lambda x: "High" if x > 4.0 else "Medium" if x > 3.2 else "Low"
        )
        st.dataframe(fallback, use_container_width=True, height=420)


def _render_executive_insights() -> None:
    insights = get_executive_insights()
    st.markdown("<div class='section-title'>Executive Insights</div>", unsafe_allow_html=True)
    if not insights:
        st.info("No executive insights generated.")
        return

    cols = st.columns(3)
    for i, item in enumerate(insights):
        sev = item["severity"]
        css = "alert-warning"
        if sev == "critical":
            css = "alert-critical"
        elif sev == "success":
            css = "alert-success"
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class='alert-card {css} fade-in'>
                  <div class='alert-title'>{item['message']}</div>
                  <div style='margin-top:8px;font-size:12px;color:#334155'><b>Business Impact:</b> {item['impact']}</div>
                  <div style='margin-top:6px;font-size:12px;color:#334155'><b>Recommended Action:</b> {item['action']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_page() -> None:
    st.markdown("<div class='page-title'>People & Workforce</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='margin-top:-8px;margin-bottom:14px;color:#64748B;font-size:13px'>"
        "Executive workforce analytics focused on productivity, labour cost, risk and performance resilience."
        "</div>",
        unsafe_allow_html=True,
    )

    _render_exec_kpi_cards()
    _render_executive_insights()

    tabs = st.tabs(
        [
            "Absence Analytics",
            "Staff Turnover",
            "Labour Cost",
            "Workforce Productivity",
            "Recruitment",
            "Health & Safety",
            "Site Comparison",
        ]
    )

    with tabs[0]:
        _render_absence_tab()
    with tabs[1]:
        _render_turnover_tab()
    with tabs[2]:
        _render_labour_tab()
    with tabs[3]:
        _render_productivity_tab()
    with tabs[4]:
        _render_recruitment_tab()
    with tabs[5]:
        _render_safety_tab()
    with tabs[6]:
        _render_site_comparison_tab()


def render() -> None:
    render_page()


def main() -> None:
    render_page()
