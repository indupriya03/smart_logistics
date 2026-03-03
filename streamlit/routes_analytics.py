# routes_analytics.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db import run_query
from queries import *
from components import kpi_card

def app(run_query):
    st.header("🛣️ Routes & Delivery Analytics")
    # ============================
    #  Key Performance Indicators
    # ============================
    col1, col2, col3, col4, col5 = st.columns(5)

    route_df=run_query(route_query)

    with col1:
        kpi_card("Total Routes", f"{route_df['route_key'].nunique():,}")
    with col2:
        kpi_card("Avg Route Distance", f"{route_df['distance_km'].mean():.2f} km")
    with col3:
        kpi_card("🚚 Avg Route Transit Time",f"{route_df['avg_transit_hours'].mean():.2f} hrs")
    with col4:
        kpi_card("⏱️ Route Delay %",f"{route_df['route_delay_pct'].mean():.2f}%",color='red')
    with col5:
        if not route_df.empty:
            most_active_route = route_df.iloc[0]
            kpi_card("Most Active Route", most_active_route['route_name'])
    st.markdown("---")

    # ====================
    # Risk Classification
    # ====================
    st.subheader("⚠️ Route Risk Classification")

    # Quantile thresholds
    critical_threshold = route_df['route_delay_pct'].quantile(0.9)
    monitor_threshold = route_df['route_delay_pct'].quantile(0.6)

    # Classify each route
    def classify_risk(x):
        if x >= critical_threshold:
            return "Critical"
        elif x >= monitor_threshold:
            return "Monitor"
        else:
            return "Healthy"

    route_df['risk_level'] = route_df['route_delay_pct'].apply(classify_risk)

    # ====================
    # Transit Delay Chart
    # ====================
    fig = px.bar(
        route_df.sort_values('route_delay_pct', ascending=False),
        x='route_name',
        y='route_delay_pct',
        color='risk_level',
        title="Route Delay % (Pickup → Delivery)",
        labels={"route_delay_pct": "Delay %", "route_name": "Route"},
        color_discrete_map={
            "Critical": "red",
            "Monitor": "orange",
            "Healthy": "green"
        }
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(range=[0, 100]),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ====================
    # Top 10 Routes Table
    # ====================
    st.subheader("🏆 Top 10 Routes by Shipment Volume")
    top_10_routes = route_df.sort_values('total_shipments', ascending=False).head(10)
    top_10_routes.reset_index(drop=True, inplace=True)
    top_10_routes['Rank'] = top_10_routes.index + 1

    # Rearrange columns
    display_cols = ['Rank', 'route_name', 'total_shipments', 'avg_transit_hours', 'route_delay_pct', 'risk_level']
    st.dataframe(
        top_10_routes[display_cols].style.format({
            'total_shipments': '{:,}',
            'avg_transit_hours': '{:.2f} hrs',
            'route_delay_pct': '{:.2f}%'
        }).background_gradient(subset=['route_delay_pct'], cmap='Reds'),
        use_container_width=True
    )