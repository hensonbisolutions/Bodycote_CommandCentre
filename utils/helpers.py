"""UI helper utilities for the Bodycote Executive Command Centre."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import streamlit as st


COLORS = {
    "primary": "#005EB8",
    "primary_dark": "#003B6D",
    "accent": "#00A3E0",
    "success": "#16A34A",
    "warning": "#F59E0B",
    "critical": "#DC2626",
    "text": "#1E293B",
    "text_secondary": "#64748B",
    "border": "#E2E8F0",
    "surface": "#FFFFFF",
    "background": "#F5F7FA",
}


_STATUS_CLASS = {
    "running": "status-running",
    "idle": "status-idle",
    "maintenance": "status-maintenance",
    "critical": "status-critical",
    "offline": "status-offline",
    "completed": "status-completed",
    "delayed": "status-delayed",
    "queued": "status-queued",
}


_PRIORITY_COLOR = {
    "critical": COLORS["critical"],
    "high": COLORS["warning"],
    "medium": COLORS["accent"],
    "low": COLORS["success"],
}


_ICON_FALLBACK = {
    "monitor_heart": "H",
    "precision_manufacturing": "M",
    "paid": "$",
    "pie_chart": "P",
    "fact_check": "Q",
    "local_shipping": "D",
    "build_circle": "T",
    "receipt_long": "R",
    "payments": "$",
    "trending_up": "U",
    "manufacturing": "M",
    "percent": "%",
    "schedule": "S",
    "verified": "V",
    "whatshot": "F",
    "health_and_safety": "A",
    "build": "T",
    "event": "E",
    "feedback": "C",
    "report": "!",
    "public": "G",
}


def _display_icon(icon: str) -> str:
    """Return a robust icon representation that does not depend on webfont loading."""
    if not icon:
        return "*"
    # If already an emoji/icon glyph, keep it.
    if any(ord(ch) > 127 for ch in icon):
        return icon
    return _ICON_FALLBACK.get(icon.strip(), "*")


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, str):
            value = value.replace("%", "").replace(",", "").replace("£", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return default


def _sparkline_svg(series: Iterable[float] | None = None, color: str = COLORS["primary"]) -> str:
    if not series:
        series = [42, 44, 43, 47, 46, 49, 50]
    values = [float(v) for v in series]
    low = min(values)
    high = max(values)
    spread = (high - low) if high != low else 1.0
    points = []
    for i, v in enumerate(values):
        x = (i / max(1, len(values) - 1)) * 100
        y = 20 - ((v - low) / spread) * 16
        points.append(f"{x:.1f},{y:.1f}")
    path = " ".join(points)
    return (
        "<svg class='sparkline' viewBox='0 0 100 24' preserveAspectRatio='none'>"
        f"<polyline fill='none' stroke='{color}' stroke-width='2.2' points='{path}' /></svg>"
    )


def format_currency(value: Any) -> str:
    amount = _to_float(value)
    if abs(amount) >= 1_000_000_000:
        return f"£{amount / 1_000_000_000:.2f}B"
    if abs(amount) >= 1_000_000:
        return f"£{amount / 1_000_000:.2f}M"
    if abs(amount) >= 1_000:
        return f"£{amount / 1_000:.1f}K"
    return f"£{amount:,.0f}"


def format_percentage(value: Any, decimals: int = 1) -> str:
    return f"{_to_float(value):.{decimals}f}%"


def format_number(value: Any) -> str:
    return f"{int(_to_float(value)):,.0f}"


def get_change_indicator(value: Any) -> tuple[str, str]:
    delta = _to_float(value)
    if delta > 0:
        return "upward", "delta-positive"
    if delta < 0:
        return "downward", "delta-negative"
    return "trending_flat", "delta-neutral"


def get_status_color(status: str) -> str:
    status = (status or "").strip().lower()
    if status in ("running", "completed"):
        return COLORS["success"]
    if status in ("idle", "queued"):
        return COLORS["accent"]
    if status == "maintenance":
        return COLORS["warning"]
    if status in ("critical", "delayed"):
        return COLORS["critical"]
    if status == "offline":
        return "#6B7280"
    return COLORS["text_secondary"]


def get_priority_color(priority: str) -> str:
    return _PRIORITY_COLOR.get((priority or "").strip().lower(), COLORS["text_secondary"])


def create_status_badge(status: str) -> str:
    label = (status or "Unknown").strip()
    css_class = _STATUS_CLASS.get(label.lower(), "status-offline")
    return f"<span class='status-pill {css_class}'>{label}</span>"


def create_priority_color(priority: str) -> str:
    label = (priority or "Unknown").strip()
    color = get_priority_color(label)
    return (
        "<span class='priority-badge' "
        f"style='color:{color};border-color:{color}33;background:{color}14'>{label}</span>"
    )


def create_metric_card(
    title: str,
    value: Any,
    delta: Any | None = None,
    target: str | None = None,
    icon: str = "monitoring",
    trend_data: Iterable[float] | None = None,
    border_color: str | None = None,
    **_: Any,
) -> None:
    if border_color is None:
        border_color = COLORS["primary"]

    direction, delta_class = get_change_indicator(delta if delta is not None else 0)
    delta_text = "No change" if delta is None else str(delta)
    spark = _sparkline_svg(trend_data, color=border_color)

    metric_icon = _display_icon(icon)

    html = f"""
    <div class='metric-card fade-in' style='border-left-color:{border_color};'>
      <div class='metric-top'>
        <div class='metric-title'>{title}</div>
                <span class='metric-icon' aria-hidden='true'>{metric_icon}</span>
      </div>
      <div class='metric-value'>{value}</div>
      <div class='metric-row'>
        <div class='metric-delta {delta_class}'>
          <span class='material-symbols-outlined' style='font-size:14px;vertical-align:middle'>{direction}</span>
          <span>{delta_text}</span>
        </div>
        <div class='target-pill'>{target or 'Target tracked'}</div>
      </div>
      {spark}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_premium_kpi_card(
    title: str,
    value: Any,
    icon: str = "monitoring",
    trend_pct: float = 0.0,
    trend_direction: str = "neutral",
    target: str = "",
) -> None:
    delta = trend_pct
    if trend_direction == "up":
        delta = abs(trend_pct)
    elif trend_direction == "down":
        delta = -abs(trend_pct)
    else:
        delta = 0

    icon_name = "monitoring"
    if icon and len(icon) < 20 and all(ord(ch) < 128 for ch in icon):
        icon_name = icon

    target_text = f"Target: {target}" if target else "Target tracked"
    create_metric_card(
        title=title,
        value=value,
        delta=f"{delta:+.1f}%",
        target=target_text,
        icon=icon_name,
    )


def create_page_title(title: str, subtitle: str = "") -> None:
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f"<div style='margin-top:-8px;margin-bottom:14px;color:{COLORS['text_secondary']};font-size:13px'>{subtitle}</div>",
            unsafe_allow_html=True,
        )


def create_insight_card(
    title: str,
    content: str,
    category: str = "info",
    icon: str = "insights",
    **_: Any,
) -> None:
    border = {
        "info": COLORS["accent"],
        "success": COLORS["success"],
        "warning": COLORS["warning"],
        "critical": COLORS["critical"],
    }.get(category, COLORS["accent"])
    st.markdown(
        f"""
        <div class='insight-card fade-in' style='border-left:4px solid {border};'>
          <div class='alert-head'>
            <div class='alert-title'>
              <span class='material-symbols-outlined' style='font-size:16px;vertical-align:middle;margin-right:6px'>{icon}</span>
              {title}
            </div>
          </div>
          <div style='color:{COLORS['text_secondary']};font-size:13px;line-height:1.55'>{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_alert_card(
    severity: str,
    timestamp: Any,
    site: str,
    summary: str,
    impact: str,
    action: str,
) -> None:
    sev = (severity or "warning").lower().strip()
    css = "alert-warning"
    icon = "warning"
    if sev in ("critical", "high"):
        css = "alert-critical"
        icon = "error"
    elif sev in ("success", "low"):
        css = "alert-success"
        icon = "task_alt"

    stamp = str(timestamp)
    st.markdown(
        f"""
        <div class='alert-card {css} fade-in'>
          <div class='alert-head'>
            <div class='alert-title'>
              <span class='material-symbols-outlined' style='font-size:16px;vertical-align:middle;margin-right:6px'>{icon}</span>
              {summary}
            </div>
            <div class='alert-meta'>{stamp}</div>
          </div>
          <div class='alert-meta' style='margin-bottom:8px'>Site: {site}</div>
          <div style='margin-bottom:6px'><strong>Impact:</strong> {impact}</div>
          <div><strong>Recommended Action:</strong> {action}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_executive_briefing(
    revenue_summary: str,
    operational_summary: str,
    risks: str,
    opportunities: str,
    health_score: str,
) -> None:
    st.markdown(
        """
        <div class='briefing-card fade-in'>
          <div class='section-title'>Executive Briefing</div>
          <div style='color:#64748B;font-size:13px'>High-level summary of current performance, risks and opportunities.</div>
          <div class='briefing-grid'>
        """,
        unsafe_allow_html=True,
    )
    for key, val in [
        ("Revenue", revenue_summary),
        ("Operations", operational_summary),
        ("Risks", risks),
        ("Opportunities", opportunities),
        ("Health Score", health_score),
    ]:
        st.markdown(
            f"<div class='briefing-item'><div class='k'>{key}</div><div class='v'>{val}</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_enterprise_header() -> None:
    today = datetime.now().strftime("%A, %d %B %Y")
    st.markdown(
        f"""
        <div class='enterprise-header'>
                    <div class='enterprise-header-inner'>
                        <div class='header-left'>
                            <div class='bodycote-logo bodycote-logo--header' aria-label='Bodycote logo'>
                                <span class='bodycote-mark'><span class='bodycote-dot'></span></span>
                                <span class='bodycote-word'>Bodycote</span>
                            </div>
                            <h1 class='header-title'>
                                <span class='title-full'>Executive Operations Command Centre</span>
                                <span class='title-short'>Command Centre</span>
                            </h1>
                            <div class='header-date'>{today}</div>
                        </div>
                        <div class='header-right'>
                            <a class='refresh-link' href='?refresh=1'>
                                <span class='material-symbols-outlined' style='font-size:14px'>refresh</span>
                                <span class='refresh-label'>Refresh</span>
                            </a>
                            <div class='header-icon'><span class='material-symbols-outlined'>notifications</span></div>
                            <div class='header-icon'><span class='material-symbols-outlined'>settings</span></div>
                            <div class='header-icon'><span class='material-symbols-outlined'>account_circle</span></div>
                        </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.markdown(
        """
        <div class='nav-logo'>
                    <div class='bodycote-logo bodycote-logo--sidebar' aria-label='Bodycote logo'>
                        <span class='bodycote-mark'><span class='bodycote-dot'></span></span>
                    </div>
          <div>
                        <div class='title'>Bodycote plc</div>
                        <div class='subtitle'>Bodycote plc · Executive Command Centre</div>
          </div>
        </div>
        <div class='nav-label'>Navigation</div>
        """,
        unsafe_allow_html=True,
    )


def apply_global_styles() -> None:
    css_path = Path(__file__).resolve().parents[1] / "assets" / "style.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def is_mobile_preview() -> bool:
        return st.session_state.get("view_mode", "Desktop") == "Mobile Preview"


def apply_view_mode_styles() -> None:
        """Apply optional mobile preview overrides without impacting desktop defaults."""
        if not is_mobile_preview():
                return

        st.markdown(
                """
                <style>
                /* Constrain content to a phone-like viewport when preview is enabled. */
                .block-container {
                    max-width: 430px !important;
                    padding-left: 0.75rem !important;
                    padding-right: 0.75rem !important;
                    padding-top: 7.6rem !important;
                }

                .enterprise-header {
                    left: 0 !important;
                    padding-left: 12px !important;
                    padding-right: 12px !important;
                    height: auto !important;
                    min-height: 64px !important;
                    align-items: flex-start !important;
                    padding-top: 8px !important;
                    padding-bottom: 8px !important;
                }

                .enterprise-header-inner,
                .header-left {
                    width: 100% !important;
                }

                .header-date,
                .header-right,
                .title-full {
                    display: none !important;
                }

                .title-short {
                    display: inline !important;
                }

                /* Force Streamlit columns to stack into one column in preview mode. */
                div[data-testid="stHorizontalBlock"] {
                    flex-direction: column !important;
                    gap: 0.6rem !important;
                }

                div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                    width: 100% !important;
                    min-width: 0 !important;
                    flex: 1 1 100% !important;
                }

                .metric-card {
                    min-height: 132px !important;
                }

                .metric-value {
                    font-size: 24px !important;
                }

                .section-title {
                    font-size: 17px !important;
                }
                </style>
                """,
                unsafe_allow_html=True,
        )
