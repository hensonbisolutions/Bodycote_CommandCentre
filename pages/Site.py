"""Site operations command centre page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils import charts
from utils.data import (
    get_daily_metrics,
    get_first_pass_yield,
    get_furnace_utilisation,
    get_furnaces,
    get_maintenance,
    get_on_time_delivery_pct,
    get_orders,
    get_sites,
)
from utils.helpers import (
    COLORS,
    create_metric_card,
    create_status_badge,
    format_currency,
    format_number,
    format_percentage,
)


def _site_lookup() -> pd.DataFrame:
    sites = get_sites().copy()
    if "site_name" not in sites.columns and "name" in sites.columns:
        sites["site_name"] = sites["name"]
    return sites


def _safe_site_name(site_row: pd.Series) -> str:
    if "site_name" in site_row:
        return str(site_row["site_name"])
    if "name" in site_row:
        return str(site_row["name"])
    return "Selected Site"


def _calc_site_health(orders: pd.DataFrame) -> float:
    if orders.empty:
        return 0.0
    completed = orders[orders["status"] == "Completed"]
    delayed = orders[orders["status"] == "Delayed"]
    on_time = 0.0
    if not completed.empty:
        c = completed.copy()
        c["completion_date"] = pd.to_datetime(c["completion_date"]).dt.date
        c["due_date"] = pd.to_datetime(c["due_date"]).dt.date
        on_time = (c["completion_date"] <= c["due_date"]).mean() * 100
    delay_penalty = (len(delayed) / max(len(orders), 1)) * 100
    health = max(0.0, min(100.0, (on_time * 0.65) + ((100 - delay_penalty) * 0.35)))
    return health


def _render_furnace_cards(furnaces: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Furnace Command Grid</div>", unsafe_allow_html=True)
    if furnaces.empty:
        st.info("No furnace data available for this site.")
        return

    display = furnaces.copy()
    if "furnace_name" not in display.columns and "furnace_id" in display.columns:
        display["furnace_name"] = display["furnace_id"]
    if "temperature" not in display.columns:
        display["temperature"] = 780
    if "runtime_hours" not in display.columns:
        display["runtime_hours"] = 14
    if "active_jobs" not in display.columns:
        display["active_jobs"] = 3
    if "utilisation_pct" not in display.columns:
        display["utilisation_pct"] = 70
    if "maintenance_due_days" not in display.columns:
        display["maintenance_due_days"] = 12

    cards_per_row = 3
    rows = [display.iloc[i : i + cards_per_row] for i in range(0, len(display), cards_per_row)]
    for chunk in rows:
        cols = st.columns(cards_per_row)
        for i, (_, row) in enumerate(chunk.iterrows()):
            with cols[i]:
                status_html = create_status_badge(str(row.get("status", "Idle")))
                util_val = float(row.get("utilisation_pct", 0))
                util_color = COLORS["success"] if util_val >= 75 else COLORS["warning"] if util_val >= 55 else COLORS["critical"]
                st.markdown(
                    f"""
                    <div class='surface-card fade-in'>
                      <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
                        <div style='font-size:13px;font-weight:700;color:#1E293B'>{row.get('furnace_name', 'Furnace')}</div>
                        {status_html}
                      </div>
                      <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>
                        <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:8px'>
                          <div style='font-size:11px;color:#64748B'>Temperature</div>
                          <div style='font-size:17px;font-weight:700'>{int(float(row.get('temperature', 0)))} C</div>
                        </div>
                        <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:8px'>
                          <div style='font-size:11px;color:#64748B'>Utilisation</div>
                          <div style='font-size:17px;font-weight:700;color:{util_color}'>{util_val:.0f}%</div>
                        </div>
                        <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:8px'>
                          <div style='font-size:11px;color:#64748B'>Runtime</div>
                          <div style='font-size:17px;font-weight:700'>{float(row.get('runtime_hours', 0)):.1f} h</div>
                        </div>
                        <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:8px'>
                          <div style='font-size:11px;color:#64748B'>Jobs</div>
                          <div style='font-size:17px;font-weight:700'>{int(float(row.get('active_jobs', 0)))}</div>
                        </div>
                      </div>
                      <div style='margin-top:8px;font-size:12px;color:#64748B'>Maintenance due in <b>{int(float(row.get('maintenance_due_days', 0)))}</b> days</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_page() -> None:
    sites = _site_lookup()
    orders = get_orders()
    furnaces = get_furnaces()
    daily = get_daily_metrics()

    st.markdown("<div class='page-title'>Site Operations Command Centre</div>", unsafe_allow_html=True)

    site_names = sites["site_name"].tolist() if "site_name" in sites.columns else []
    selected_name = st.selectbox("Select Site", options=site_names, index=0 if site_names else None)
    if not selected_name:
        st.warning("No site data available.")
        return

    site_row = sites[sites["site_name"] == selected_name].iloc[0]
    site_id = site_row["site_id"] if "site_id" in site_row else selected_name

    site_orders = orders[orders["site_id"] == site_id].copy() if "site_id" in orders.columns else orders.copy()
    site_furnaces = furnaces[furnaces["site_id"] == site_id].copy() if "site_id" in furnaces.columns else furnaces.copy()
    site_daily = daily[daily["site_id"] == site_id].copy() if "site_id" in daily.columns else daily.copy()

    health = _calc_site_health(site_orders)
    site_revenue = site_orders["revenue"].sum() if "revenue" in site_orders.columns else 0
    availability = ((site_furnaces["status"].isin(["Running", "Idle"])).mean() * 100) if not site_furnaces.empty and "status" in site_furnaces.columns else 0

    cards = st.columns(4)
    with cards[0]:
        create_metric_card("Site Health Score", f"{health:.0f}/100", delta="+1.6%", target="Target: 85+", icon="monitor_heart", border_color=COLORS["accent"])
    with cards[1]:
        create_metric_card("Equipment Availability", format_percentage(availability), delta="+0.7%", target="Target: 92%", icon="precision_manufacturing")
    with cards[2]:
        create_metric_card("Production Revenue", format_currency(site_revenue), delta="+3.1%", target="Target: +4%", icon="paid")
    with cards[3]:
        create_metric_card("Resource Utilisation", format_percentage(get_furnace_utilisation(site_id)), delta="+1.9%", target="Target: 85%", icon="pie_chart")

    cards2 = st.columns(4)
    with cards2[0]:
        create_metric_card("Quality", format_percentage(get_first_pass_yield(site_id)), delta="+0.8%", target="Target: 95%", icon="fact_check", border_color=COLORS["success"])
    with cards2[1]:
        create_metric_card("Delivery", format_percentage(get_on_time_delivery_pct(site_id)), delta="-0.4%", target="Target: 95%", icon="local_shipping", border_color=COLORS["warning"])
    with cards2[2]:
        maintenance_df = get_maintenance().copy()
        if "status" in maintenance_df.columns:
            open_maint = len(maintenance_df[maintenance_df["status"].isin(["Scheduled", "In Progress", "Open"])])
        else:
            # Fallback for datasets without maintenance status: treat recent events as active workload.
            if "date_scheduled" in maintenance_df.columns:
                maintenance_df["date_scheduled"] = pd.to_datetime(maintenance_df["date_scheduled"], errors="coerce").dt.date
                cutoff_date = (pd.Timestamp.today() - pd.Timedelta(days=30)).date()
                open_maint = len(maintenance_df[maintenance_df["date_scheduled"] >= cutoff_date])
            else:
                open_maint = len(maintenance_df)
        create_metric_card("Maintenance", format_number(open_maint), delta="-2", target="Target: < 20", icon="build_circle", border_color=COLORS["warning"])
    with cards2[3]:
        create_metric_card("Orders", format_number(len(site_orders)), delta="+4", target="Stable pipeline", icon="receipt_long")

    chart_cols = st.columns(2)
    with chart_cols[0]:
        if not site_daily.empty:
            st.plotly_chart(charts.quality_trend_chart(site_daily), use_container_width=True)
        else:
            st.info("No quality trend data available.")
    with chart_cols[1]:
        if not site_daily.empty:
            st.plotly_chart(charts.delivery_performance_trend(site_daily), use_container_width=True)
        else:
            st.info("No delivery trend data available.")

    _render_furnace_cards(site_furnaces)

    st.markdown("<div class='section-title'>Orders</div>", unsafe_allow_html=True)
    search = st.text_input("Search orders", placeholder="Order ID, process, material")
    status_filter = st.multiselect("Status", options=sorted(site_orders["status"].dropna().unique().tolist()) if "status" in site_orders.columns else [])
    priority_filter = st.multiselect("Priority", options=sorted(site_orders["priority"].dropna().unique().tolist()) if "priority" in site_orders.columns else [])

    filtered = site_orders.copy()
    if search:
        term = search.lower()
        mask = False
        for col in ["order_id", "material", "process", "customer_name"]:
            if col in filtered.columns:
                mask = mask | filtered[col].astype(str).str.lower().str.contains(term, na=False)
        filtered = filtered[mask]
    if status_filter and "status" in filtered.columns:
        filtered = filtered[filtered["status"].isin(status_filter)]
    if priority_filter and "priority" in filtered.columns:
        filtered = filtered[filtered["priority"].isin(priority_filter)]

    st.dataframe(filtered, use_container_width=True, height=380)
    st.download_button(
        "Export Site Orders CSV",
        data=filtered.to_csv(index=False),
        file_name=f"{selected_name.lower().replace(' ', '_')}_orders.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render() -> None:
    render_page()


def main() -> None:
    render_page()
