import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
from db import run_query
from queries import *
from components import kpi_card


# ============
# PAGE CONFIG
# ============
st.set_page_config(
    page_title="Smart Logistics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🚚Smart Logistics Management & Analytics")


    
# ===================
# SIDEBAR NAVIGATION
# ===================
st.sidebar.title("Navigation")
# Page Navigation
page=st.sidebar.radio(
    "Go to",
    [
        "Homepage", 
        "Warehouse Analytics", 
        "Routes & Delivery Analytics", 
        "Costs & Financial Analytics",
        "Courier Performance"
    ]
)
# ===================================
# Shipment Tracking Search in Sidebar
# ===================================
st.sidebar.markdown("---")
st.sidebar.subheader("🔎 Shipment Tracking")
shipment_key_input=st.sidebar.text_input("Enter Shipment Key")
if shipment_key_input:
    # Fetch Shipment Details
    shipment_df=run_query(shipment_search_query,params={"shipment_id": shipment_key_input})

    if shipment_df.empty:
        st.warning("❌ No shipment found with this key.")
    else:
        st.markdown("**Shipment Details**")
        st.dataframe(shipment_df)

        #Fetch tracking History
        tracking_df=run_query(tracking_query,params={"shipment_id": shipment_key_input})
        # Render tracking chart on main page if tracking_df exists
        if tracking_df.empty:
            st.info("ℹ️ No tracking events found. Shipment may be Cancelled or not yet picked up.")
        else:
            st.markdown("**Tracking History**")
            fig = px.scatter(
                tracking_df,
                x="timestamp",
                y="status",
                title="Shipment Timeline",
                labels={"timestamp": "Time", "status": "Status"},
                color="status"
            )
            fig.update_traces(marker=dict(size=12))
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
if page == "Homepage":
    st.header("📊 Dashboard Overview")
    # ==========
    # CORE KPIs
    # ==========
    st.markdown("#### 📦 Operational Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    kpi_df = run_query(kpi_query)

    total_shipments = kpi_df.iloc[0]["total_shipments"]
    delivered = kpi_df.iloc[0]["delivered_count"]
    cancelled = kpi_df.iloc[0]["cancelled_count"]

    delivered_percent = round((delivered / total_shipments) * 100, 2) if total_shipments > 0 else 0
    cancelled_percent = round((cancelled / total_shipments) * 100, 2) if total_shipments > 0 else 0
     
    with col1:
        kpi_card("Total Shipments", f"{int(total_shipments):,}",color='#1f77b4')
    with col2:
        kpi_card("Delivered%", f"{delivered_percent}%",color='green')
    with col3:
        kpi_card("Cancelled%", f"{cancelled_percent}%",color='red')
    with col4:

        pending_df=run_query(pending_query)
        pending_shipments=pending_df.iloc[0]['pending_shipments']
        pending_percent=round((pending_shipments/total_shipments)*100,2)
        kpi_card("Pending Shipments", f"{pending_percent}%",color="#ff9800")
    with col5:

        active_df=run_query(active_couriers_query)
        active_couriers=active_df.iloc[0]['active_couriers']
        kpi_card("Active Couriers", f"{active_couriers:,}")

    st.markdown("---")
    # ==========================
    # DELIVERY PERFORMANCE KPIs
    # ==========================
    st.markdown("#### ⚙️ Performance & Efficiency")

    col6,col7,col8,col9=st.columns(4)
    with col6:
        avg_pickup_df=run_query(avg_pickup_query)
        avg_pickup_days=avg_pickup_df.iloc[0]['avg_pickup_days']
        kpi_card("Avg Pickup Time", f"{int(round(avg_pickup_days))} days",color='#1f77b4')
    with col7:
        avg_delivery_df=run_query(avg_delivery_query)
        avg_delivery_days=avg_delivery_df.iloc[0]['avg_delivery_days']
        kpi_card("Avg Delivery Time", f"{int(round(avg_delivery_days))} days",color="#1f77b4")
    with col8:

        delayed_df=run_query(delayed_query)
        delayed_shipments=delayed_df.iloc[0]['delayed_shipments']
        kpi_card("Delayed Shipments", f"{int(delayed_shipments):,}",color='red')
    with col9:
        operational_cost_query="""
            SELECT SUM(fuel_cost+labor_cost+misc_cost) AS total_cost
            FROM costs;
        """
        operational_cost_df=run_query(operational_cost_query)
        operational_costs=operational_cost_df.iloc[0]['total_cost']
        kpi_card("Total Operational Cost", f"${int(operational_costs):,}")

    st.markdown("---")
    # ===============================
    # TOP PERFORMERS
    # ===============================
    left,right=st.columns(2)
    # ===============================
    # LEFT COLUMN: Operational Leaders
    # ===============================
    with left:
        st.subheader("🏆 Operation Leaders")
        # --- Top Courier ---
        st.write("Top Courier")
        top_courier_df = get_top_couriers(limit=1)
        if not top_courier_df.empty:
            courier = top_courier_df.iloc[0]
            st.write(f"🏅 **{courier['courier_name']}** — {courier['Shipments_handled']} shipments, Avg Time: {courier['Avg_delivery_hours']} hrs, Rating: {courier['Rating']}")
        else:
            st.write("🏅 No data available")
        
        # --- Top Warehouse ---
        st.write("Top Warehouse")
        
        top_warehouse_df = run_query(top_warehouse_query)
        if not top_warehouse_df.empty:
            warehouse = top_warehouse_df.iloc[0]
            st.write(f"🏭 **{warehouse['warehouse_city']}** — {warehouse['shipments_handled']} shipments, Avg_dispatch Time: {warehouse['avg_dispatch_hours']}, Utilised: {warehouse['capacity_utilization_pct']}% capacity ")
        else:
            st.write("🏭 No data available")
        st.write("Best Vehicle")
        # --- Best Vehicle ---
        
        best_vehicle_df = run_query(best_vehicle_query)
        if not best_vehicle_df.empty:
            vehicle = best_vehicle_df.iloc[0]
            st.write(f"🚛 **{vehicle['vehicle_type']}** — {vehicle['shipments_handled']} shipments")
        else:
            st.write("🚛 No data available")  
    # ===============================
    # RIGHT COLUMN: Business Leaders
    # ===============================
    with right:
        st.subheader("📍 Business Leaders")
        # --- Top Origin City ---
        st.write("Top Origin City")
              

        top_origin_df = run_query(top_origin_query)
        if not top_origin_df.empty:
            origin = top_origin_df.iloc[0]
            st.write(f"📦 **{origin['city']}** — {origin['total_orders']} orders placed")
        else:
            st.write("📦 No data available")
    
        # --- Top Destination City ---
        st.write("Top Destination City")

        top_dest_df = run_query(top_dest_query)
        if not top_dest_df.empty:
            dest = top_dest_df.iloc[0]
            st.write(f"🏁 **{dest['city']}** — {dest['total_delivered']} orders delivered")
        else:
            st.write("🏁 No data available")
        
        st.write("Best Month")   
        # --- Best Month ---

        best_month_df = run_query(best_month_query)
        if not best_month_df.empty:
            month = best_month_df.iloc[0]
            st.write(f"📅 **{month['month']}** — {month['total_orders']} orders placed")
        else:
            st.write("📅 No data available")
    st.markdown("---")

    # ======================
    # SHIPPING TRENDS CHART
    # ======================
    st.markdown("## 📈 Shipping Trends Over Time")


    trends_df = run_query(shipping_trends_query)
    # Calculate percentages
    trends_df['delivered_pct'] = trends_df['delivered'] / trends_df['total_shipments'] * 100
    trends_df['cancelled_pct'] = trends_df['cancelled'] / trends_df['total_shipments'] * 100
    trends_df['in_transit_pct'] = trends_df['in_transit'] / trends_df['total_shipments'] * 100
    #Create stacked bar chart
         
    if not trends_df.empty:
        fig_stack_pct = go.Figure()
        statuses = {
            "Delivered": ("delivered_pct","green"),
            "Cancelled": ("cancelled_pct","red"),
            "In Transit": ("in_transit_pct","orange")
        }

        for label, (column, color) in statuses.items():
            fig_stack_pct.add_trace(go.Bar(
                x=trends_df['month'],
                y=trends_df[column],
                name=label,
                marker_color=color,
                text=trends_df[column].apply(lambda x: f'{x:.1f}%'),  # Show % label
                textposition='inside',  # inside the bar
                hovertemplate='%{y:.1f}% '+label+'<extra></extra>'
            ))

        # Optional: Add total shipments as a line
        fig_stack_pct.add_trace(go.Scatter(
            x=trends_df['month'],
            y=trends_df['total_shipments'],
            mode='lines+markers',
            name='Total Shipments',
            line=dict(color='blue', width=2, dash='dash'),
            yaxis='y2',  # Use secondary y-axis
            hovertemplate='%{y} Total Shipments<extra></extra>'
        ))

        # Layout with secondary y-axis for total shipments
        fig_stack_pct.update_layout(
            title='Monthly Shipment Efficiency & Total Shipments',
            xaxis_title='Month',
           yaxis=dict(title='Percentage of Shipments (%)', range=[0, 100]),
            yaxis2=dict(title='Total Shipments', overlaying='y', side='right'),
            barmode='stack',
            template='plotly_white',
            hovermode='x unified'
        )
        # Render in Streamlit
        st.plotly_chart(fig_stack_pct, use_container_width=True)
    else:
        st.write("📅 No data available")
 
    # ================
    # TOP 10 COURIERS
    # ================
    st.subheader("🚚 Top 10 Performing Couriers")
    top_10_couriers_df = get_top_couriers(limit=10)
    top_10_couriers_df['On_Time_Delivery'] = top_10_couriers_df['On_Time_Delivery'].round(2)
    if top_10_couriers_df.empty:
        st.info("No courier data available.")
    else:
        top_10_couriers_df = top_10_couriers_df.reset_index(drop=True)
        top_10_couriers_df.index = top_10_couriers_df.index + 1
        # Display nicely formatted table
        st.dataframe(
            top_10_couriers_df.style.format({
                "Shipments_handled": "{:,}",
                "Avg_delivery_hours": "{:.2f} hrs",
                "On_Time_Delivery": "{:.2f}%",
                "Avg_cost_per_shipment": "${:.2f}",
                "Rating": "{:.1f}"
            },),
            use_container_width=True
        )
elif page == "Warehouse Analytics":
    import warehouse_analytics
    warehouse_analytics.app(run_query)  # pass run_query to the page
elif page == "Routes & Delivery Analytics":
    import routes_analytics
    routes_analytics.app(run_query)
elif page == "Costs & Financial Analytics":   
    import cost_analytics
    cost_analytics.app(run_query)
elif page == "Courier Performance":   
    import courier_analytics
    courier_analytics.app(run_query)