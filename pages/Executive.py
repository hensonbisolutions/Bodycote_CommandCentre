"""Executive dashboard page."""

from __future__ import annotations

from typing import Iterable

import streamlit as st

from utils import charts
from utils.data import (
    get_complaints,
    get_complaints_count,
    get_daily_metrics,
    get_first_pass_yield,
    get_furnace_utilisation,
    get_furnaces,
    get_gross_margin,
    get_maintenance,
    get_mtd_revenue,
    get_on_time_delivery_pct,
    get_orders,
    get_orders_running,
    get_revenue_by_process,
    get_revenue_by_region,
    get_revenue_trend,
    get_executive_forecast,
    get_safety_incidents,
    get_site_performance,
    get_sites,
    get_top_customers,
    get_ytd_revenue,
)
from utils.helpers import (
    COLORS,
    create_alert_card,
    create_executive_briefing,
    create_metric_card,
    format_currency,
    format_number,
    format_percentage,
)


def _render_kpis() -> None:
    mtd = get_mtd_revenue()
    ytd = get_ytd_revenue()
    running = get_orders_running()
    on_time = get_on_time_delivery_pct()
    fpy = get_first_pass_yield()
    util = get_furnace_utilisation()
    margin = get_gross_margin()
    safety = get_safety_incidents()

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        create_metric_card("Revenue MTD", format_currency(mtd), delta="+4.2%", target="Target: +5%", icon="payments")
    with kpi_cols[1]:
        create_metric_card("Revenue YTD", format_currency(ytd), delta="+7.8%", target="Target: +8%", icon="trending_up")
    with kpi_cols[2]:
        create_metric_card("Orders Running", format_number(running), delta="-1.1%", target="Target: < 180", icon="manufacturing")
    with kpi_cols[3]:
        create_metric_card("Gross Margin", format_percentage(margin), delta="+1.3%", target="Target: 45%", icon="percent")

    kpi_cols_2 = st.columns(4)
    with kpi_cols_2[0]:
        create_metric_card("On-Time Delivery", format_percentage(on_time), delta="+0.9%", target="Target: 95%", icon="schedule", border_color=COLORS["accent"])
    with kpi_cols_2[1]:
        create_metric_card("First Pass Yield", format_percentage(fpy), delta="+1.2%", target="Target: 95%", icon="verified", border_color=COLORS["success"])
    with kpi_cols_2[2]:
        create_metric_card("Furnace Utilisation", format_percentage(util), delta="+2.4%", target="Target: 85%", icon="whatshot", border_color=COLORS["warning"])
    with kpi_cols_2[3]:
        create_metric_card("Safety Incidents", format_number(safety), delta="-12%", target="Target: 0", icon="health_and_safety", border_color=COLORS["critical"])


def _render_briefing() -> None:
    forecast = get_executive_forecast()
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        create_executive_briefing(
            revenue_summary="MTD above prior period trend",
            operational_summary="Capacity stable with selective constraints",
            risks="Late orders concentrated in three sites",
            opportunities="Aerospace margin expansion across North",
            health_score="82 / 100",
        )
    with right:
        risk = int(forecast.get("risk_score", 0))
        risk_color = COLORS["success"] if risk < 35 else COLORS["warning"] if risk < 65 else COLORS["critical"]
        st.markdown(
            f"""
            <div class='surface-card fade-in' style='border-left:4px solid {risk_color}; min-height: 220px'>
              <div class='section-title' style='font-size:16px;margin-bottom:8px'>Executive Forecast</div>
              <div style='display:flex;justify-content:space-between;margin-bottom:8px'>
                <div style='color:#64748B;font-size:12px'>Overall Outlook</div>
                <div style='font-weight:700;color:#1E293B'>{forecast.get('outlook', 'Stable')}</div>
              </div>
              <div style='display:flex;justify-content:space-between;margin-bottom:8px'>
                <div style='color:#64748B;font-size:12px'>Business Risk Score</div>
                <div style='font-weight:800;color:{risk_color}'>{risk} / 100</div>
              </div>
              <div style='display:flex;justify-content:space-between;margin-bottom:8px'>
                <div style='color:#64748B;font-size:12px'>Forecast Confidence</div>
                <div style='font-weight:700;color:#1E293B'>{forecast.get('confidence', 0)}%</div>
              </div>
              <div style='display:flex;justify-content:space-between;margin-bottom:10px'>
                <div style='color:#64748B;font-size:12px'>Time Horizon</div>
                <div style='font-weight:700;color:#1E293B'>{forecast.get('horizon', 'Next 30 Days')}</div>
              </div>
              <div style='font-size:11px;color:#64748B;line-height:1.45'>
                Forecasts are generated using historical trend analysis and simulated demonstration data. They are intended solely to demonstrate predictive dashboard capabilities.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _sparkline(series: Iterable[float], color: str) -> str:
    values = [float(v) for v in series] if series else [1, 2, 3, 2, 4]
    low = min(values)
    high = max(values)
    spread = (high - low) if high != low else 1
    points = []
    for i, value in enumerate(values):
        x = (i / max(1, len(values) - 1)) * 100
        y = 20 - ((value - low) / spread) * 16
        points.append(f"{x:.1f},{y:.1f}")
    path = " ".join(points)
    return (
        "<svg class='sparkline' viewBox='0 0 100 24' preserveAspectRatio='none'>"
        f"<polyline fill='none' stroke='{color}' stroke-width='2.0' points='{path}' /></svg>"
    )


def _risk_css(level: str) -> tuple[str, str]:
    if level == "Red":
        return COLORS["critical"], "status-critical"
    if level == "Amber":
        return COLORS["warning"], "status-maintenance"
    return COLORS["success"], "status-running"


def _render_predictive_insights() -> None:
    forecast = get_executive_forecast()
    cards = forecast.get("predictive_cards", [])
    if not cards:
        return

    st.markdown("<div class='section-title'>Predictive Insights</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, card in enumerate(cards[:8]):
        color, badge = _risk_css(card.get("risk", "Green"))
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class='surface-card fade-in' style='border-left:4px solid {color};min-height:250px'>
                  <div style='display:flex;justify-content:space-between;gap:8px;align-items:center'>
                    <div style='font-weight:700;color:#1E293B'>{card.get('title')}</div>
                    <span class='status-pill {badge}'>{card.get('risk')}</span>
                  </div>
                  <div style='font-size:22px;font-weight:800;color:#0F172A;margin-top:8px'>{card.get('predicted_value')}</div>
                  <div style='font-size:12px;color:#64748B;margin-top:6px'>Confidence: {card.get('confidence')}% · Horizon: {card.get('horizon')}</div>
                  <div style='font-size:12px;color:#334155;margin-top:8px'><b>Impact:</b> {card.get('impact')}</div>
                  <div style='font-size:12px;color:#334155;margin-top:6px'><b>Action:</b> {card.get('action')}</div>
                  {_sparkline(card.get('spark', []), color)}
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_outlook_and_risk_matrix() -> None:
    forecast = get_executive_forecast()
    left, right = st.columns([1.5, 1], gap="large")
    with left:
        st.markdown("<div class='section-title'>Executive Outlook Summary</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='surface-card fade-in' style='line-height:1.65;color:#334155'>{forecast.get('outlook_summary')}</div>",
            unsafe_allow_html=True,
        )
    with right:
        risk_matrix = forecast.get("risk_matrix")
        if risk_matrix is not None and not risk_matrix.empty:
            st.plotly_chart(charts.risk_matrix_heatmap(risk_matrix), use_container_width=True)
            st.dataframe(risk_matrix, use_container_width=True, hide_index=True, height=248)


def _render_alerts() -> None:
    st.markdown("<div class='section-title'>Executive Alerts</div>", unsafe_allow_html=True)
    alerts = [
        {
            "severity": "critical",
            "timestamp": "10m ago",
            "site": "Birmingham",
            "summary": "Heat treatment line outage",
            "impact": "Potential delay to 12 high-priority orders",
            "action": "Reroute to Coventry and dispatch field engineer",
        },
        {
            "severity": "warning",
            "timestamp": "42m ago",
            "site": "Sheffield",
            "summary": "On-time delivery below threshold",
            "impact": "Service level risk for strategic customer account",
            "action": "Activate expedited logistics window for queued jobs",
        },
        {
            "severity": "success",
            "timestamp": "1h ago",
            "site": "Derby",
            "summary": "Quality recovery sustained",
            "impact": "FPY above target for 7 consecutive days",
            "action": "Replicate setup across adjacent plants",
        },
    ]
    cols = st.columns(3)
    for i, alert in enumerate(alerts):
        with cols[i]:
            create_alert_card(**alert)


def _render_charts() -> None:
    revenue_trend = get_revenue_trend(120)
    site_perf = get_site_performance()
    region_perf = get_revenue_by_region()
    process_perf = get_revenue_by_process()
    daily = get_daily_metrics()
    maintenance = get_maintenance()
    orders = get_orders()
    top_customers = get_top_customers(20)
    sites = get_sites()

    st.markdown("<div class='section-title'>Operational Performance</div>", unsafe_allow_html=True)
    row1 = st.columns(2)
    with row1[0]:
        st.plotly_chart(charts.revenue_trend_chart(revenue_trend), use_container_width=True)
    with row1[1]:
        st.plotly_chart(charts.delivery_performance_trend(daily), use_container_width=True)

    row2 = st.columns(2)
    with row2[0]:
        st.plotly_chart(charts.site_performance_chart(site_perf), use_container_width=True)
    with row2[1]:
        st.plotly_chart(charts.regional_performance_chart(region_perf), use_container_width=True)

    row3 = st.columns(2)
    with row3[0]:
        st.plotly_chart(charts.quality_trend_chart(daily), use_container_width=True)
    with row3[1]:
        st.plotly_chart(charts.process_mix_chart(process_perf), use_container_width=True)

    row4 = st.columns(2)
    with row4[0]:
        st.plotly_chart(charts.backlog_chart(orders), use_container_width=True)
    with row4[1]:
        st.plotly_chart(charts.maintenance_trend_chart(maintenance), use_container_width=True)

    row5 = st.columns(2)
    with row5[0]:
        st.plotly_chart(charts.customer_revenue_chart(top_customers), use_container_width=True)
    with row5[1]:
        furnaces = get_furnaces()
        if "furnace_name" not in furnaces.columns and "furnace_id" in furnaces.columns:
            furnaces = furnaces.copy()
            furnaces["furnace_name"] = furnaces["furnace_id"]
        if "utilisation_pct" not in furnaces.columns:
            furnaces = furnaces.copy()
            furnaces["utilisation_pct"] = 70
        st.plotly_chart(charts.furnace_utilisation_chart(furnaces), use_container_width=True)

    map_fig = charts.site_performance_map(sites, site_perf)
    if map_fig.data:
        st.plotly_chart(map_fig, use_container_width=True)


def _render_exports() -> None:
    st.markdown("<div class='section-title'>Data Exports</div>", unsafe_allow_html=True)
    orders = get_orders()
    site_perf = get_site_performance()
    customers = get_top_customers(50)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("Export Orders CSV", data=orders.to_csv(index=False), file_name="orders_export.csv", mime="text/csv", use_container_width=True)
    with c2:
        st.download_button("Export Site Performance CSV", data=site_perf.to_csv(index=False), file_name="site_performance_export.csv", mime="text/csv", use_container_width=True)
    with c3:
        st.download_button("Export Customers CSV", data=customers.to_csv(index=False), file_name="customers_export.csv", mime="text/csv", use_container_width=True)


def render_page() -> None:
    st.markdown("<div class='page-title'>Executive Dashboard</div>", unsafe_allow_html=True)
    _render_briefing()
    _render_kpis()
    _render_alerts()
    _render_predictive_insights()
    _render_outlook_and_risk_matrix()
    _render_charts()
    _render_exports()


def render() -> None:
    render_page()


def main() -> None:
    render_page()
