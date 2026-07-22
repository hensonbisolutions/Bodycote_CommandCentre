"""
Orders Page - Searchable and filterable order management
"""

import streamlit as st
import pandas as pd
from utils import data as data_utils
from utils import charts as chart_utils
from utils.helpers import create_status_badge, create_priority_color, COLORS, create_page_title
from datetime import datetime, timedelta


def show_page():
    """Display orders page"""
    
    # Page title
    create_page_title("Order Management", "Search, filter, and analyze all orders")
    
    # Get data
    orders = data_utils.get_orders().copy()
    sites = data_utils.get_sites()
    customers = data_utils.get_customers()
    
    # Prepare data
    orders["completion_date"] = pd.to_datetime(orders["completion_date"])
    orders["received_date"] = pd.to_datetime(orders["received_date"])
    orders["due_date"] = pd.to_datetime(orders["due_date"])
    
    st.divider()
    
    # Search and filter section
    st.markdown("### Search & Filter")
    
    search_col1, search_col2, search_col3 = st.columns([1, 1, 1])
    
    with search_col1:
        search_term = st.text_input(
            "Search Orders",
            placeholder="Order ID, Customer, Material...",
            key="order_search"
        )
    
    with search_col2:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=90), datetime.now()),
            key="order_date_range"
        )
    
    with search_col3:
        show_count = st.selectbox(
            "Show",
            [10, 25, 50, 100, 250, 500],
            key="order_show_count"
        )
    
    # Advanced filters
    st.markdown("### Advanced Filters")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        selected_customers = st.multiselect(
            "Customers",
            customers["customer_name"].unique(),
            key="order_customer_filter"
        )
    
    with filter_col2:
        selected_sites = st.multiselect(
            "Sites",
            sites["site_name"].unique(),
            key="order_site_filter"
        )
    
    with filter_col3:
        selected_statuses = st.multiselect(
            "Status",
            orders["status"].unique(),
            default=orders["status"].unique(),
            key="order_status_filter"
        )
    
    with filter_col4:
        selected_priorities = st.multiselect(
            "Priority",
            orders["priority"].unique(),
            default=orders["priority"].unique(),
            key="order_priority_filter"
        )
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        selected_processes = st.multiselect(
            "Processes",
            orders["process"].unique(),
            key="order_process_filter"
        )
    
    with filter_col2:
        selected_quality = st.multiselect(
            "Quality Result",
            orders["quality_result"].unique(),
            default=orders["quality_result"].unique(),
            key="order_quality_filter"
        )
    
    with filter_col3:
        selected_regions = st.multiselect(
            "Regions",
            sites["region"].unique(),
            key="order_region_filter"
        )
    
    # Apply filters
    filtered_orders = orders.copy()
    
    # Search filter
    if search_term:
        search_mask = (
            filtered_orders["order_id"].str.contains(search_term, case=False, na=False) |
            filtered_orders["material"].str.contains(search_term, case=False, na=False) |
            filtered_orders["process"].str.contains(search_term, case=False, na=False)
        )
        filtered_orders = filtered_orders[search_mask]
    
    # Date range filter
    if date_range and len(date_range) == 2:
        date_start = pd.Timestamp(date_range[0])
        date_end = pd.Timestamp(date_range[1])
        filtered_orders = filtered_orders[
            (filtered_orders["received_date"] >= date_start) &
            (filtered_orders["received_date"] <= date_end)
        ]
    
    # Customer filter
    if selected_customers:
        customer_ids = customers[customers["customer_name"].isin(selected_customers)]["customer_id"].values
        filtered_orders = filtered_orders[filtered_orders["customer_id"].isin(customer_ids)]
    
    # Site filter
    if selected_sites:
        site_ids = sites[sites["site_name"].isin(selected_sites)]["site_id"].values
        filtered_orders = filtered_orders[filtered_orders["site_id"].isin(site_ids)]
    
    # Region filter
    if selected_regions:
        site_ids = sites[sites["region"].isin(selected_regions)]["site_id"].values
        filtered_orders = filtered_orders[filtered_orders["site_id"].isin(site_ids)]
    
    # Status filter
    if selected_statuses:
        filtered_orders = filtered_orders[filtered_orders["status"].isin(selected_statuses)]
    
    # Priority filter
    if selected_priorities:
        filtered_orders = filtered_orders[filtered_orders["priority"].isin(selected_priorities)]
    
    # Process filter
    if selected_processes:
        filtered_orders = filtered_orders[filtered_orders["process"].isin(selected_processes)]
    
    # Quality filter
    if selected_quality:
        filtered_orders = filtered_orders[filtered_orders["quality_result"].isin(selected_quality)]
    
    # Sort
    filtered_orders = filtered_orders.sort_values("received_date", ascending=False)
    
    st.divider()
    
    # Display results
    st.markdown(f"### Results: {len(filtered_orders)} orders")
    
    # Limit display
    display_orders = filtered_orders.head(show_count).copy()
    
    # Add customer names
    display_orders = display_orders.merge(
        customers[["customer_id", "customer_name"]],
        on="customer_id",
        how="left"
    )
    
    # Format for display
    display_df = pd.DataFrame({
        "Order ID": display_orders["order_id"],
        "Customer": display_orders["customer_name"],
        "Site": display_orders["site_id"],
        "Process": display_orders["process"],
        "Material": display_orders["material"],
        "Weight (kg)": display_orders["weight_kg"].round(1),
        "Status": display_orders["status"],
        "Priority": display_orders["priority"],
        "Received": display_orders["received_date"].dt.strftime("%Y-%m-%d"),
        "Due": display_orders["due_date"].dt.strftime("%Y-%m-%d"),
        "Revenue": display_orders["revenue"].apply(lambda x: f"£{x:,.0f}"),
        "Quality": display_orders["quality_result"],
    })
    
    # Custom display with colors
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=500,
    )
    
    st.divider()
    
    # Summary statistics
    st.markdown("### Summary Statistics")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        total_revenue = filtered_orders["revenue"].sum()
        st.metric("Total Revenue", f"£{total_revenue:,.0f}")
    
    with summary_col2:
        avg_margin = filtered_orders["margin"].mean()
        st.metric("Avg Margin", f"£{avg_margin:,.0f}")
    
    with summary_col3:
        completed_count = len(filtered_orders[filtered_orders["status"] == "Completed"])
        on_time = len(filtered_orders[
            (filtered_orders["status"] == "Completed") &
            (filtered_orders["completion_date"] <= filtered_orders["due_date"])
        ])
        on_time_pct = (on_time / completed_count * 100) if completed_count > 0 else 0
        st.metric("On-Time Delivery", f"{on_time_pct:.1f}%")
    
    with summary_col4:
        passed = len(filtered_orders[filtered_orders["quality_result"] == "Pass"])
        total = len(filtered_orders[filtered_orders["status"] == "Completed"])
        fpy = (passed / total * 100) if total > 0 else 0
        st.metric("First Pass Yield", f"{fpy:.1f}%")
    
    st.divider()
    
    # Status breakdown
    st.markdown("### Status Breakdown")
    
    status_summary = filtered_orders["status"].value_counts()
    
    status_col1, status_col2 = st.columns([1, 2])
    
    with status_col1:
        for status, count in status_summary.items():
            st.markdown(f"**{status}:** {count}")
    
    with status_col2:
        # Create bar chart
        import plotly.express as px
        fig = px.bar(
            x=status_summary.index,
            y=status_summary.values,
            labels={"x": "Status", "y": "Count"},
            color=status_summary.index,
        )
        fig.update_layout(
            showlegend=False,
            height=300,
        )
        fig = chart_utils.apply_template(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Export filtered data
    st.markdown("### Export")
    
    csv = filtered_orders.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Orders",
        data=csv,
        file_name=f"bodycote_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
    
    # Order detail viewer
    st.markdown("### Order Detail")
    
    order_to_view = st.selectbox(
        "Select an order to view details",
        display_orders["order_id"].values,
        key="order_detail_selector"
    )
    
    if order_to_view:
        order_detail = filtered_orders[filtered_orders["order_id"] == order_to_view].iloc[0]
        
        st.markdown(f"#### {order_to_view}")
        
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        
        with detail_col1:
            st.markdown(f"**Customer:** {order_detail['customer_id']}")
            st.markdown(f"**Site:** {order_detail['site_id']}")
            st.markdown(f"**Process:** {order_detail['process']}")
        
        with detail_col2:
            st.markdown(f"**Material:** {order_detail['material']}")
            st.markdown(f"**Weight:** {order_detail['weight_kg']:.2f} kg")
            st.markdown(f"**Furnace:** {order_detail['furnace_id']}")
        
        with detail_col3:
            st.markdown(f"**Status:** {order_detail['status']}")
            st.markdown(f"**Priority:** {order_detail['priority']}")
            st.markdown(f"**Quality:** {order_detail['quality_result']}")
        
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        
        with detail_col1:
            st.markdown(f"**Received:** {order_detail['received_date'].strftime('%Y-%m-%d')}")
            st.markdown(f"**Due:** {order_detail['due_date'].strftime('%Y-%m-%d')}")
            if order_detail['completion_date'] and not pd.isna(order_detail['completion_date']):
                st.markdown(f"**Completed:** {order_detail['completion_date'].strftime('%Y-%m-%d')}")
        
        with detail_col2:
            st.markdown(f"**Revenue:** £{order_detail['revenue']:,.2f}")
            st.markdown(f"**Cost:** £{order_detail['cost']:,.2f}")
            st.markdown(f"**Margin:** £{order_detail['margin']:,.2f}")
        
        with detail_col3:
            margin_pct = (order_detail['margin'] / order_detail['revenue'] * 100) if order_detail['revenue'] > 0 else 0
            st.markdown(f"**Margin %:** {margin_pct:.1f}%")
            st.markdown(f"**Operator:** {order_detail['operator_id']}")
