"""Plotly chart builders with a unified enterprise style."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


COLORS = {
    "primary": "#005EB8",
    "primary_dark": "#003B6D",
    "accent": "#00A3E0",
    "success": "#16A34A",
    "warning": "#F59E0B",
    "critical": "#DC2626",
    "text": "#1E293B",
    "grid": "#E2E8F0",
    "surface": "#FFFFFF",
}


def _first_available(df: pd.DataFrame, candidates: list[str], default: str | None = None) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return default


def apply_template(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font=dict(family="Plus Jakarta Sans, Segoe UI, sans-serif", color=COLORS["text"], size=12),
        margin=dict(l=24, r=20, t=54, b=30),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, linecolor=COLORS["grid"], tickfont=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2F7", zeroline=False, tickfont=dict(size=11))
    return fig


def revenue_trend_chart(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["date"],
            y=d["revenue"],
            mode="lines",
            line=dict(color=COLORS["primary"], width=3),
            fill="tozeroy",
            fillcolor="rgba(0, 94, 184, 0.10)",
            name="Revenue",
        )
    )
    fig.update_layout(title=dict(text="Revenue Trend", x=0), yaxis_title="Revenue")
    return apply_template(fig)


def site_performance_chart(site_df: pd.DataFrame) -> go.Figure:
    x_col = _first_available(site_df, ["site_name", "site_id"], "site_id")
    color_col = _first_available(site_df, ["on_time_delivery_pct", "on_time_delivery"], "revenue")
    if x_col not in site_df.columns:
        return apply_template(go.Figure())
    fig = px.bar(
        site_df,
        x=x_col,
        y="revenue",
        color=color_col,
        color_continuous_scale=[[0, "#DC2626"], [0.5, "#F59E0B"], [1, "#16A34A"]],
    )
    fig.update_layout(title=dict(text="Site Performance", x=0), xaxis_title="Site", yaxis_title="Revenue")
    return apply_template(fig)


def regional_performance_chart(df: pd.DataFrame) -> go.Figure:
    if isinstance(df, pd.Series):
        df = df.reset_index()
        df.columns = ["region", "revenue"]
    if "region" not in df.columns or "revenue" not in df.columns:
        return apply_template(go.Figure())
    fig = px.pie(df, names="region", values="revenue", hole=0.55)
    fig.update_traces(marker=dict(colors=["#005EB8", "#00A3E0", "#16A34A", "#F59E0B", "#DC2626"]))
    fig.update_layout(title=dict(text="Regional Revenue Mix", x=0))
    return apply_template(fig)


def process_mix_chart(df: pd.DataFrame) -> go.Figure:
    if isinstance(df, pd.Series):
        tmp = df.reset_index()
        tmp.columns = ["process", "revenue"]
        tmp["gross_margin_pct"] = 0
        df = tmp
    if "process" not in df.columns or "revenue" not in df.columns:
        return apply_template(go.Figure())
    if "gross_margin_pct" not in df.columns:
        df = df.copy()
        df["gross_margin_pct"] = 0
    fig = px.treemap(df, path=["process"], values="revenue", color="gross_margin_pct", color_continuous_scale="Blues")
    fig.update_layout(title=dict(text="Process Mix", x=0), margin=dict(l=10, r=10, t=48, b=10))
    return apply_template(fig)


def furnace_utilisation_chart(df: pd.DataFrame) -> go.Figure:
    safe = df.copy()
    if "furnace_name" not in safe.columns and "furnace_id" in safe.columns:
        safe["furnace_name"] = safe["furnace_id"]
    if "furnace_name" not in safe.columns:
        safe["furnace_name"] = [f"Furnace {i+1}" for i in range(len(safe))]
    if "utilisation_pct" not in safe.columns:
        safe["utilisation_pct"] = 0
    if "status" not in safe.columns:
        safe["status"] = "Unknown"
    fig = px.bar(safe, x="furnace_name", y="utilisation_pct", color="status")
    fig.update_layout(title=dict(text="Furnace Utilisation", x=0), yaxis_title="Utilisation %")
    fig.add_hline(y=85, line_dash="dash", line_color=COLORS["warning"])
    return apply_template(fig)


def order_status_chart(df: pd.DataFrame) -> go.Figure:
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.bar(status_counts, x="status", y="count", color="status")
    fig.update_layout(title=dict(text="Order Status", x=0), xaxis_title="Status", yaxis_title="Orders")
    return apply_template(fig)


def quality_trend_chart(daily_metrics: pd.DataFrame) -> go.Figure:
    daily_metrics = daily_metrics.copy()
    daily_metrics["date"] = pd.to_datetime(daily_metrics["date"]).dt.date
    cutoff_date = (pd.Timestamp.today() - pd.Timedelta(days=90)).date()
    recent_metrics = daily_metrics[daily_metrics["date"] >= cutoff_date]
    quality_trend = recent_metrics.groupby("date")["quality_first_pass"].mean().reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=quality_trend["date"],
            y=quality_trend["quality_first_pass"],
            mode="lines",
            line=dict(color=COLORS["success"], width=3),
            fill="tozeroy",
            fillcolor="rgba(22, 163, 74, 0.12)",
            name="First Pass Yield",
        )
    )
    fig.add_hline(y=95, line_dash="dash", line_color=COLORS["warning"])
    fig.update_layout(title=dict(text="Quality Trend", x=0), yaxis_title="FPY %")
    return apply_template(fig)


def on_time_delivery_chart(df: pd.DataFrame) -> go.Figure:
    x_col = _first_available(df, ["site_name", "site_id"], "site_id")
    metric = _first_available(df, ["on_time_delivery_pct", "on_time_delivery"], "revenue")
    if x_col not in df.columns:
        return apply_template(go.Figure())
    fig = px.bar(df, x=x_col, y=metric, color=metric, color_continuous_scale="Blues")
    fig.add_hline(y=95, line_dash="dash", line_color=COLORS["warning"])
    fig.update_layout(title=dict(text="On-Time Delivery by Site", x=0), yaxis_title="On-Time %")
    return apply_template(fig)


def customer_revenue_chart(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(df.head(15), x="customer_name", y="revenue", color="revenue", color_continuous_scale="Blues")
    fig.update_layout(title=dict(text="Top Customers by Revenue", x=0), xaxis_title="Customer", yaxis_title="Revenue")
    return apply_template(fig)


def maintenance_trend_chart(maintenance_df: pd.DataFrame) -> go.Figure:
    maintenance_df = maintenance_df.copy()
    maintenance_df["date_scheduled"] = pd.to_datetime(maintenance_df["date_scheduled"]).dt.date
    cutoff_date = (pd.Timestamp.today() - pd.Timedelta(days=90)).date()
    recent = maintenance_df[maintenance_df["date_scheduled"] >= cutoff_date]
    trend = recent.groupby("date_scheduled").size().reset_index(name="count")
    fig = px.bar(trend, x="date_scheduled", y="count", color_discrete_sequence=[COLORS["warning"]])
    fig.update_layout(title=dict(text="Maintenance Trend", x=0), xaxis_title="Date", yaxis_title="Events")
    return apply_template(fig)


def backlog_chart(df: pd.DataFrame) -> go.Figure:
    if "status" not in df.columns:
        return apply_template(go.Figure())
    backlog = df[df["status"].isin(["Queued", "Running", "Delayed", "In Progress"])].copy()
    site_col = _first_available(backlog, ["site_name", "site_id"], "site_id")
    if site_col not in backlog.columns:
        return apply_template(go.Figure())
    by_site = backlog.groupby(site_col).size().reset_index(name="orders")
    fig = px.bar(by_site, x=site_col, y="orders", color="orders", color_continuous_scale="Blues")
    fig.update_layout(title=dict(text="Backlog by Site", x=0), yaxis_title="Orders")
    return apply_template(fig)


def delivery_performance_trend(daily_metrics: pd.DataFrame) -> go.Figure:
    daily_metrics = daily_metrics.copy()
    daily_metrics["date"] = pd.to_datetime(daily_metrics["date"]).dt.date
    cutoff_date = (pd.Timestamp.today() - pd.Timedelta(days=90)).date()
    recent = daily_metrics[daily_metrics["date"] >= cutoff_date]
    trend = recent.groupby("date")["on_time_delivery_pct"].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend["date"],
            y=trend["on_time_delivery_pct"],
            mode="lines",
            line=dict(color=COLORS["accent"], width=3),
            fill="tozeroy",
            fillcolor="rgba(0, 163, 224, 0.12)",
            name="On-Time Delivery",
        )
    )
    fig.add_hline(y=95, line_dash="dash", line_color=COLORS["warning"])
    fig.update_layout(title=dict(text="Delivery Performance Trend", x=0), yaxis_title="On-Time %")
    return apply_template(fig)


def site_performance_map(sites_df: pd.DataFrame, site_perf_df: pd.DataFrame) -> go.Figure:
    merged = sites_df.copy()
    if "site_id" in merged.columns and "site_id" in site_perf_df.columns:
        merged = merged.merge(site_perf_df, on="site_id", how="left", suffixes=("", "_perf"))

    lat_col = "latitude" if "latitude" in merged.columns else "lat" if "lat" in merged.columns else None
    lon_col = "longitude" if "longitude" in merged.columns else "lon" if "lon" in merged.columns else None
    name_col = "site_name" if "site_name" in merged.columns else "name" if "name" in merged.columns else None

    if not lat_col or not lon_col or not name_col:
        return go.Figure()

    color_metric = _first_available(merged, ["on_time_delivery_pct", "on_time_delivery", "first_pass_yield"])
    size_metric = _first_available(merged, ["revenue", "utilisation"])
    if color_metric is None:
        merged["kpi_color"] = 90
        color_metric = "kpi_color"
    if size_metric is None:
        merged["kpi_size"] = 1
        size_metric = "kpi_size"

    fig = px.scatter_mapbox(
        merged,
        lat=lat_col,
        lon=lon_col,
        hover_name=name_col,
        hover_data={color_metric: True, size_metric: True},
        color=color_metric,
        size=size_metric,
        color_continuous_scale=[[0, "#DC2626"], [0.5, "#F59E0B"], [1, "#16A34A"]],
        zoom=4.6,
        height=420,
    )
    fig.update_layout(
        title=dict(text="Site Performance Map", x=0),
        mapbox_style="carto-darkmatter",
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(title=color_metric.replace("_", " ").title()),
    )
    return fig
