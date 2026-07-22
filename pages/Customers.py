"""
Customers Page - Customer analytics and management
"""

import streamlit as st
import pandas as pd
from utils import data as data_utils
from utils import charts
from utils.helpers import format_currency, format_percentage, COLORS, create_premium_kpi_card, create_page_title
from datetime import datetime, timedelta


def show_page():
    """Display customers page"""
    
    # Page title
    create_page_title("Customer Analytics", "Performance metrics and order tracking")
    
    # Get data
    customers = data_utils.get_customers()
    orders = data_utils.get_orders()
    complaints = data_utils.get_complaints()
    sites = data_utils.get_sites()
    
    st.divider()
    
    # Customer selector
    st.markdown("### Customer Selection")
    
    # Get top customers
    top_customers = data_utils.get_top_customers(n=20)
    
    selected_customer = st.selectbox(
        "Select Customer",
        top_customers["customer_name"].unique(),
        key="customer_selector"
    )
    
    # Get customer data
    customer_data = customers[customers["customer_name"] == selected_customer].iloc[0]
    customer_id = customer_data["customer_id"]
    
    # Customer header
    st.markdown(f"### {selected_customer}")
    
    header_col1, header_col2, header_col3, header_col4 = st.columns(4)
    
    with header_col1:
        st.markdown(f"**Customer ID:** {customer_id}")
        st.markdown(f"**Type:** {customer_data['customer_type']}")
    
    with header_col2:
        st.markdown(f"**Country:** {customer_data['country']}")
        st.markdown(f"**Annual Spend:** £{customer_data['annual_spend']:,.0f}")
    
    with header_col3:
        customer_revenue = data_utils.get_customer_revenue(customer_id)
        st.markdown(f"**YTD Revenue:** £{customer_revenue:,.0f}")
        st.markdown(f"**% of Total:** {(customer_revenue / orders[orders['status'] == 'Completed']['revenue'].sum() * 100):.1f}%")
    
    with header_col4:
        customer_orders = orders[orders["customer_id"] == customer_id]
        completed_orders = len(customer_orders[customer_orders["status"] == "Completed"])
        running_orders = len(customer_orders[customer_orders["status"] == "In Progress"])
        st.markdown(f"**Completed Orders:** {completed_orders}")
        st.markdown(f"**Running Orders:** {running_orders}")
    
    st.divider()
    
    # Customer KPIs
    st.markdown("## Customer Performance Metrics")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    # Calculate metrics
    customer_completed = customer_orders[customer_orders["status"] == "Completed"]
    
    with kpi_col1:
        total_revenue = customer_completed["revenue"].sum()
        create_premium_kpi_card(
            title="Total Revenue",
            value=format_currency(total_revenue),
            icon="💷",
            trend_pct=0,
            trend_direction="neutral",
            target=""
        )
    
    with kpi_col2:
        total_cost = customer_completed["cost"].sum()
        total_margin = total_revenue - total_cost
        margin_pct = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
        create_premium_kpi_card(
            title="Gross Margin %",
            value=f"{margin_pct:.1f}%",
            icon="💰",
            trend_pct=0,
            trend_direction="neutral",
            target=""
        )
    
    with kpi_col3:
        on_time = len(customer_completed[customer_completed["completion_date"] <= customer_completed["due_date"]])
        on_time_pct = (on_time / len(customer_completed) * 100) if len(customer_completed) > 0 else 0
        create_premium_kpi_card(
            title="On-Time Delivery %",
            value=f"{on_time_pct:.1f}%",
            icon="⚡",
            trend_pct=(on_time_pct - 95),
            trend_direction="up" if on_time_pct > 95 else "down",
            target="95%"
        )
    
    with kpi_col4:
        passed = len(customer_completed[customer_completed["quality_result"] == "Pass"])
        fpy_pct = (passed / len(customer_completed) * 100) if len(customer_completed) > 0 else 0
        create_premium_kpi_card(
            title="First Pass Yield %",
            value=f"{fpy_pct:.1f}%",
            icon="✅",
            trend_pct=(fpy_pct - 95),
            trend_direction="up" if fpy_pct > 95 else "down",
            target="95%"
        )
    
    st.divider()
    
    # Customer orders
    st.markdown("## Customer Orders")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        order_status_filter = st.multiselect(
            "Filter by Status",
            customer_orders["status"].unique(),
            default=customer_orders["status"].unique(),
            key="customer_order_status"
        )
    
    with filter_col2:
        order_priority_filter = st.multiselect(
            "Filter by Priority",
            customer_orders["priority"].unique(),
            default=customer_orders["priority"].unique(),
            key="customer_order_priority"
        )
    
    with filter_col3:
        order_quality_filter = st.multiselect(
            "Filter by Quality",
            customer_orders["quality_result"].unique(),
            default=customer_orders["quality_result"].unique(),
            key="customer_order_quality"
        )
    
    # Apply filters
    filtered_customer_orders = customer_orders[
        (customer_orders["status"].isin(order_status_filter)) &
        (customer_orders["priority"].isin(order_priority_filter)) &
        (customer_orders["quality_result"].isin(order_quality_filter))
    ].copy()
    
    # Display orders
    display_orders = filtered_customer_orders[[
        "order_id", "process", "material", "weight_kg", "status", 
        "priority", "received_date", "due_date", "completion_date", 
        "revenue", "quality_result"
    ]].copy()
    
    display_orders["received_date"] = display_orders["received_date"].astype(str)
    display_orders["due_date"] = display_orders["due_date"].astype(str)
    display_orders["completion_date"] = display_orders["completion_date"].astype(str)
    display_orders["revenue"] = display_orders["revenue"].apply(lambda x: f"£{x:,.0f}")
    display_orders["weight_kg"] = display_orders["weight_kg"].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(
        display_orders,
        use_container_width=True,
        hide_index=True,
        height=400,
    )
    
    st.divider()
    
    # Analytics
    st.markdown("## Analytics")
    
    analytics_col1, analytics_col2 = st.columns(2)
    
    with analytics_col1:
        # Revenue by process
        revenue_by_process = filtered_customer_orders.groupby("process")["revenue"].sum().sort_values(ascending=False)
        
        st.markdown("### Revenue by Process")
        st.bar_chart(revenue_by_process)
    
    with analytics_col2:
        # Orders by status
        orders_by_status = filtered_customer_orders["status"].value_counts()
        
        st.markdown("### Orders by Status")
        st.bar_chart(orders_by_status)
    
    # Quality breakdown
    st.markdown("### Quality Breakdown")
    
    quality_col1, quality_col2, quality_col3 = st.columns(3)
    
    total_orders_customer = len(filtered_customer_orders)
    
    with quality_col1:
        passed = len(filtered_customer_orders[filtered_customer_orders["quality_result"] == "Pass"])
        st.metric("Passed", f"{passed}/{total_orders_customer}", f"{(passed/total_orders_customer*100):.1f}%")
    
    with quality_col2:
        rework = len(filtered_customer_orders[filtered_customer_orders["quality_result"] == "Rework"])
        st.metric("Rework", f"{rework}/{total_orders_customer}", f"{(rework/total_orders_customer*100):.1f}%")
    
    with quality_col3:
        reject = len(filtered_customer_orders[filtered_customer_orders["quality_result"] == "Reject"])
        st.metric("Reject", f"{reject}/{total_orders_customer}", f"{(reject/total_orders_customer*100):.1f}%")
    
    st.divider()
    
    # Complaints
    st.markdown("## Customer Complaints")
    
    customer_complaints = complaints[complaints["customer_id"] == customer_id]
    
    if len(customer_complaints) > 0:
        complaint_col1, complaint_col2 = st.columns([1, 2])
        
        with complaint_col1:
            st.markdown(f"**Total Complaints:** {len(customer_complaints)}")
            
            complaint_types = customer_complaints["complaint_type"].value_counts()
            st.markdown("**By Type:**")
            for comp_type, count in complaint_types.items():
                st.markdown(f"- {comp_type}: {count}")
        
        with complaint_col2:
            st.markdown("**Complaint History:**")
            
            for _, complaint in customer_complaints.iterrows():
                severity_color = {
                    "Critical": "🔴",
                    "High": "🟠",
                    "Medium": "🟡",
                    "Low": "🟢"
                }.get(complaint["severity"], "⚪")
                
                status_symbol = {
                    "Open": "🔵",
                    "In Review": "🟡",
                    "Resolved": "🟢",
                    "Closed": "⚪"
                }.get(complaint["status"], "⚪")
                
                st.markdown(
                    f"""
                    {severity_color} {status_symbol} **{complaint['complaint_type']}**
                    - {complaint['date_raised']}
                    - {complaint['description'][:80]}...
                    """
                )
    else:
        st.markdown("✅ **No complaints for this customer**")
    
    st.divider()
    
    # Revenue trend
    st.markdown("## Revenue Trend")
    
    customer_daily_revenue = filtered_customer_orders.groupby("received_date")["revenue"].sum().reset_index()
    customer_daily_revenue.columns = ["date", "revenue"]
    customer_daily_revenue["date"] = pd.to_datetime(customer_daily_revenue["date"])
    customer_daily_revenue = customer_daily_revenue.sort_values("date")
    
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=customer_daily_revenue["date"],
        y=customer_daily_revenue["revenue"],
        fill="tozeroy",
        fillcolor="rgba(0, 163, 224, 0.2)",
        line=dict(color=COLORS["accent"], width=2),
        hovertemplate="<b>%{x|%b %d}</b><br>Revenue: £%{y:,.0f}<extra></extra>",
    ))
    
    fig.update_layout(
        title="Customer Revenue Trend",
        xaxis_title="Date",
        yaxis_title="Revenue (£)",
        height=400,
    )
    fig = charts.apply_template(fig)

    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Sites working with this customer
    st.markdown("## Sites Processing Orders")
    
    sites_working = filtered_customer_orders["site_id"].unique()
    sites_data = sites[sites["site_id"].isin(sites_working)]
    
    sites_col1, sites_col2 = st.columns([1, 1])
    
    with sites_col1:
        for _, site in sites_data.iterrows():
            site_order_count = len(filtered_customer_orders[filtered_customer_orders["site_id"] == site["site_id"]])
            site_revenue = filtered_customer_orders[filtered_customer_orders["site_id"] == site["site_id"]]["revenue"].sum()
            
            st.markdown(
                f"""
                **{site['site_name']}**
                - Orders: {site_order_count}
                - Revenue: £{site_revenue:,.0f}
                """
            )
    
    with sites_col2:
        st.markdown("**Site Performance:**")
        for _, site in sites_data.iterrows():
            site_orders = filtered_customer_orders[filtered_customer_orders["site_id"] == site["site_id"]]
            if len(site_orders) > 0:
                on_time_site = len(site_orders[site_orders["completion_date"] <= site_orders["due_date"]])
                on_time_pct_site = (on_time_site / len(site_orders) * 100) if len(site_orders) > 0 else 0
                st.markdown(f"- {site['site_name']}: {on_time_pct_site:.0f}% on-time")
    
    st.divider()
    
    # Export
    st.markdown("## Export")
    
    csv = filtered_customer_orders.to_csv(index=False)
    st.download_button(
        label="📥 Download Customer Orders",
        data=csv,
        file_name=f"bodycote_{selected_customer.replace(' ', '_')}_orders_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
