import streamlit as st
import plotly.express as px
from db import run_query
from queries import *
from components import kpi_card

# Each page has a main function
def app(run_query):
    st.header("🏭 Warehouse Analytics")

    # =====
    # KPIs
    # =====
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3 = st.columns(3)

    
    with col1:
        # ================
        # TOTAL WAREHOUSES 
        # ================
        warehouse_count_df=run_query(warehouse_count_query)
        warehouse_count = warehouse_count_df.iloc[0]['warehouse_count']
        kpi_card("Total Warehouses", f"{warehouse_count:,}")
    with col2:
        # ========================
        # AVG CAPACITY UTILISATION 
        # ========================
        avg_utilization_df=run_query(avg_utilization_query)
        avg_utilization=avg_utilization_df.iloc[0]['avg_capacity_utilization']
        kpi_card("Avg Capacity Utilization", f"{avg_utilization:.2f}%")
    with col3:
        # ==================
        # AVG DISPATCH TIME 
        # ==================
        avg_dispatch_df=run_query(avg_dispatch_query)
        avg_dispatch=avg_dispatch_df.iloc[0]['avg_dispatch_hours']
        kpi_card("Avg Dispatch Time", f"{avg_dispatch:.2f} hrs")
    st.markdown("---")

    col4,col5=st.columns(2)
    with col4:
        # ====================
        # HIGHEST CANCELLATION 
        # ====================
        cancel_df = run_query(cancel_query)
        total_cancelled = cancel_df['cancelled_shipments'].sum()
        avg_cancel_rate = cancel_df['cancellation_rate_pct'].mean()
        worst_wh = cancel_df.iloc[0]   # sorted desc
        kpi_card("🔥 Highest Cancellation", 
             f"{worst_wh['warehouse_city']} ({worst_wh['cancellation_rate_pct']}%)",
             color="red")
    with col5:
        # ====================
        # LOWEST CANCELLATION 
        # ====================
        best_wh = cancel_df.iloc[-1]
        kpi_card("🏆 Lowest Cancellation", 
            f"{best_wh['warehouse_city']} ({best_wh['cancellation_rate_pct']}%)",
            color="green")

    st.markdown("---")
    # =======================
    # WAREHOUSE LOAD ANALYSIS
    # =======================
    st.subheader("📦 Warehouse Load Analysis")
    warehouse_load_df=run_query(warehouse_load_query)
    fig_load = px.bar(
        warehouse_load_df,
        x="warehouse_city",
        y="total_shipments",
        title="High-Traffic Warehouse Cities (Total Shipments)",
        labels={"warehouse_city": "Warehouse", "total_shipments": "Total Shipments"},
        color="total_shipments",
        color_continuous_scale="Blues"
    )
    fig_load.update_traces(
        hovertemplate="%{x}: %{y:,} shipments<extra></extra>"
    )
    st.plotly_chart(fig_load, use_container_width=True)
    st.markdown("---")

    # =======================
    # WAREHOUSE RANKING TABLE 
    # =======================   
    st.markdown("#### 🏆 Top 5 High-Traffic Warehouse Cities")
    top_5 = warehouse_load_df.head(5).copy()
    top_5.reset_index(drop=True, inplace=True)
    top_5["Rank"] = top_5.index + 1

    # Rearrange columns
    top_5 = top_5[["Rank", "warehouse_city", "total_shipments"]]

    # Display nicely formatted table
    st.dataframe(
        top_5.style.format({"total_shipments": "{:,}"})
               .background_gradient(subset=["total_shipments"], cmap="Blues"),hide_index=True,
                use_container_width=True
    )
    st.markdown("---")
    # ==============================
    # CANCELLATION RATE BY WAREHOUSE
    # ==============================
    st.markdown("#### 📉 Cancellation Rate By Warehouse")

    fig = px.bar(
        cancel_df,
        x='warehouse_city',
        y='cancellation_rate_pct',
        title='Cancellation Rate by Warehouse',
        labels={'cancellation_rate_pct':'Cancellation Rate (%)'},
        color='cancellation_rate_pct',
        color_continuous_scale='Reds'
    )

    st.plotly_chart(fig, use_container_width=True)
    # ====================================
    # CONTRIBUTION TO TOTAL NETWORK DELAYS 
    # ====================================
    def classify_delay(x):
        if x >= critical_threshold:
            return "Critical"
        elif x >= monitor_threshold:
            return "Monitor"
        else:
            return "Healthy"
    st.markdown("#### ⏱️ Warehouse Delay Impact")
    delayed_shipments_by_city_df=run_query(delayed_shipments_by_city_query)
    critical_threshold = delayed_shipments_by_city_df["contribution_to_total_delays_pct"].quantile(0.9)
    monitor_threshold = delayed_shipments_by_city_df["contribution_to_total_delays_pct"].quantile(0.6)
    delayed_shipments_by_city_df["risk_level"] = delayed_shipments_by_city_df["contribution_to_total_delays_pct"].apply(classify_delay)

    fig = px.bar(
        delayed_shipments_by_city_df,
        x="city",
        y="contribution_to_total_delays_pct",
        color='risk_level',
        title="Warehouse Contribution to Total Network Delays (%)",
        labels={"contribution_to_total_delays_pct": "Contribution %"},
        color_discrete_map={
            "Critical":"red",
            "Monitor":"orange",
            "Healthy":"green"
        }
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    # ==============================
    # WAREHOUSE CAPACITY COMPARISON 
    # ==============================   
    st.subheader("🏭 Warehouse Capacity Comparison")

    warehouse_capacity_df=run_query(warehouse_capacity_query)
    fig_capacity = px.bar(
        warehouse_capacity_df,
        x="warehouse_city",
        y="capacity_utilization_pct",
        text="capacity_utilization_pct",
        title="Warehouse Capacity Utilization (%)",
        labels={"warehouse_city": "Warehouse", "capacity_utilization_pct": "Utilization %"},
        color="capacity_utilization_pct",
        color_continuous_scale="Viridis"
    )

    fig_capacity.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig_capacity, use_container_width=True)

    
