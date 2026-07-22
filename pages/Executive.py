"""Executive dashboard page."""

from __future__ import annotations

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
    create_executive_briefing(
        revenue_summary="MTD above prior period trend",
        operational_summary="Capacity stable with selective constraints",
        risks="Late orders concentrated in three sites",
        opportunities="Aerospace margin expansion across North",
        health_score="82 / 100",
    )


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
    _render_charts()
    _render_exports()


def render() -> None:
    render_page()


def main() -> None:
    render_page()
