"""Regions performance page."""

from __future__ import annotations

import streamlit as st

from utils import charts
from utils.data import get_revenue_by_region, get_site_performance
from utils.helpers import create_metric_card, format_currency, format_percentage


def _region_kpis(region_df, selected_region: str) -> None:
    total_revenue = region_df["revenue"].sum() if "revenue" in region_df.columns else 0
    top_region = "N/A"
    if not region_df.empty and "region" in region_df.columns:
        top_region = region_df.sort_values("revenue", ascending=False).iloc[0]["region"]

    cards = st.columns(3)
    with cards[0]:
        create_metric_card("Regional Revenue", format_currency(total_revenue), delta="+2.1%", target="Target: +4%", icon="payments")
    with cards[1]:
        create_metric_card("Top Region", str(top_region), delta="Stable", target="Benchmark", icon="public")
    with cards[2]:
        site_perf = get_site_performance()
        if "region" in site_perf.columns and selected_region != "All Regions":
            site_perf = site_perf[site_perf["region"] == selected_region]
        on_time_col = "on_time_delivery" if "on_time_delivery" in site_perf.columns else None
        on_time = site_perf[on_time_col].mean() if on_time_col and not site_perf.empty else 0
        create_metric_card("Avg On-Time", format_percentage(on_time), delta="+0.6%", target="Target: 95%", icon="schedule")


def render_page() -> None:
    st.markdown("<div class='page-title'>Regional Operations</div>", unsafe_allow_html=True)

    region_df = get_revenue_by_region().copy()
    if "region" not in region_df.columns:
        st.warning("Regional data is unavailable in the current dataset.")
        return

    region_options = ["All Regions"] + sorted(region_df["region"].dropna().astype(str).unique().tolist())
    selected_region = st.selectbox("Select Region", region_options)

    filtered_region_df = region_df.copy()
    site_perf = get_site_performance().copy()

    if selected_region != "All Regions":
        filtered_region_df = filtered_region_df[filtered_region_df["region"] == selected_region]
        if "region" in site_perf.columns:
            site_perf = site_perf[site_perf["region"] == selected_region]

    _region_kpis(filtered_region_df, selected_region)

    row = st.columns(2)
    with row[0]:
        st.plotly_chart(charts.regional_performance_chart(filtered_region_df), use_container_width=True)
    with row[1]:
        st.plotly_chart(charts.site_performance_chart(site_perf), use_container_width=True)

    st.markdown("<div class='section-title'>Regional Site Performance</div>", unsafe_allow_html=True)
    st.dataframe(site_perf, use_container_width=True, height=380)


def render() -> None:
    render_page()


def main() -> None:
    render_page()
