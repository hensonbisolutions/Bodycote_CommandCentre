"""Maintenance operations page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils import charts
from utils.data import get_furnaces, get_maintenance, get_sites
from utils.helpers import create_metric_card, format_currency, format_number


def _prepare_maintenance() -> pd.DataFrame:
    maintenance = get_maintenance().copy()
    furnaces = get_furnaces().copy()
    sites = get_sites().copy()

    if "date_scheduled" in maintenance.columns:
        maintenance["date_scheduled"] = pd.to_datetime(maintenance["date_scheduled"], errors="coerce")

    if "furnace_id" in maintenance.columns and "furnace_id" in furnaces.columns:
        maintenance = maintenance.merge(
            furnaces[[c for c in ["furnace_id", "site_id", "furnace_name"] if c in furnaces.columns]],
            on="furnace_id",
            how="left",
        )

    site_name_col = "site_name" if "site_name" in sites.columns else "name" if "name" in sites.columns else None
    if site_name_col and "site_id" in maintenance.columns and "site_id" in sites.columns:
        maintenance = maintenance.merge(
            sites[["site_id", site_name_col]].rename(columns={site_name_col: "site_name"}),
            on="site_id",
            how="left",
        )

    if "site_name" not in maintenance.columns:
        maintenance["site_name"] = "Unknown Site"

    return maintenance


def _render_kpis(df: pd.DataFrame) -> None:
    total_events = len(df)
    total_cost = df["cost"].sum() if "cost" in df.columns else 0
    avg_duration = df["duration_hours"].mean() if "duration_hours" in df.columns and len(df) > 0 else 0

    recent_count = 0
    if "date_scheduled" in df.columns:
        cutoff = pd.Timestamp.today() - pd.Timedelta(days=30)
        recent_count = len(df[df["date_scheduled"] >= cutoff])

    cards = st.columns(4)
    with cards[0]:
        create_metric_card("Maintenance Events", format_number(total_events), delta="+3", target="Target: Balanced", icon="build")
    with cards[1]:
        create_metric_card("Last 30 Days", format_number(recent_count), delta="-2", target="Target: < 60", icon="event")
    with cards[2]:
        create_metric_card("Total Cost", format_currency(total_cost), delta="+1.4%", target="Target: Controlled", icon="payments")
    with cards[3]:
        create_metric_card("Avg Duration", f"{avg_duration:.1f} h", delta="-0.5h", target="Target: < 12h", icon="schedule")


def render_page() -> None:
    st.markdown("<div class='page-title'>Maintenance Command Centre</div>", unsafe_allow_html=True)
    maintenance = _prepare_maintenance()

    if maintenance.empty:
        st.info("No maintenance records available.")
        return

    site_options = ["All Sites"] + sorted(maintenance["site_name"].dropna().astype(str).unique().tolist())
    selected_site = st.selectbox("Site", options=site_options)

    filtered = maintenance.copy()
    if selected_site != "All Sites":
        filtered = filtered[filtered["site_name"] == selected_site]

    _render_kpis(filtered)

    st.plotly_chart(charts.maintenance_trend_chart(filtered), use_container_width=True)

    st.markdown("<div class='section-title'>Maintenance Records</div>", unsafe_allow_html=True)
    display_cols = [
        c
        for c in [
            "maintenance_id",
            "site_name",
            "furnace_id",
            "furnace_name",
            "maintenance_type",
            "date_scheduled",
            "duration_hours",
            "cost",
            "notes",
        ]
        if c in filtered.columns
    ]
    st.dataframe(filtered[display_cols], use_container_width=True, height=420)


def render() -> None:
    render_page()


def main() -> None:
    render_page()
