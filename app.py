"""Bodycote Executive Operations Command Centre - enterprise shell."""

from __future__ import annotations

import importlib
from typing import Any

import streamlit as st

from utils.helpers import apply_global_styles, render_enterprise_header, render_sidebar_brand


st.set_page_config(
    page_title="Bodycote Executive Operations Command Centre",
    page_icon="B",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _init_state() -> None:
    defaults = {
        "refresh_key": 0,
        "selected_site": None,
        "selected_customer": None,
        "selected_order": None,
        "nav_page": "Dashboard",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _render_module(module: Any) -> None:
    for fn_name in ("render", "render_page", "show", "show_page", "main", "app"):
        fn = getattr(module, fn_name, None)
        if callable(fn):
            fn()
            return
    st.error("No valid render function found for selected page module.")


def _get_nav_items() -> list[tuple[str, str, str]]:
    return [
        ("Dashboard", "📊", "pages.Executive"),
        ("Regions", "🌍", "pages.Regions"),
        ("Sites", "🏭", "pages.Site"),
        ("Customers", "👥", "pages.Customers"),
        ("Orders", "🧾", "pages.Orders"),
        ("Quality", "✅", "pages.Quality"),
        ("Maintenance", "🛠️", "pages.Maintenance"),
        ("Settings", "⚙️", "pages.Executive"),
    ]


def _render_sidebar() -> str:
    with st.sidebar:
        render_sidebar_brand()
        items = _get_nav_items()
        selected = st.session_state.get("nav_page", "Dashboard")
        labels = [item[0] for item in items]
        label_to_icon = {label: icon for label, icon, _ in items}

        option_labels = [f"{label_to_icon[label]} {label}" for label in labels]
        selected_index = labels.index(selected) if selected in labels else 0
        chosen = st.radio(
            "Navigation",
            options=option_labels,
            index=selected_index,
            key="nav_radio",
            label_visibility="collapsed",
        )
        chosen_label = chosen.split(" ", 1)[1] if " " in chosen else chosen
        st.session_state["nav_page"] = chosen_label
        st.markdown("<div style='margin-top:16px;color:#64748B;font-size:11px'>Enterprise operations navigation</div>", unsafe_allow_html=True)
    return st.session_state.get("nav_page", "Dashboard")


def _resolve_module_path(nav_page: str) -> str:
    for label, _, mod in _get_nav_items():
        if label == nav_page:
            return mod
    return "pages.Executive"


def main() -> None:
    _init_state()
    apply_global_styles()
    render_enterprise_header()
    selected = _render_sidebar()

    # Existing functionality is preserved by routing to current page modules.
    module_path = _resolve_module_path(selected)
    module = importlib.import_module(module_path)

    if selected in {"Settings"}:
        st.markdown(
            f"<div class='surface-card fade-in' style='margin-bottom:12px'><b>{selected}</b> is presented through the closest operational dashboard module in this release.</div>",
            unsafe_allow_html=True,
        )

    _render_module(module)


if __name__ == "__main__":
    main()
