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
    # Top 5 routes per risk level
    # ====================
    top_n = 5
    critical_routes = route_df[route_df['risk_level'] == 'Critical'].sort_values('route_delay_pct', ascending=False).head(top_n)
    monitor_routes = route_df[route_df['risk_level'] == 'Monitor'].sort_values('route_delay_pct', ascending=False).head(top_n)
    healthy_routes = route_df[route_df['risk_level'] == 'Healthy'].sort_values('route_delay_pct', ascending=False).head(top_n)

    # ====================
    # Create 3 columns
    # ====================
    col1, col2, col3 = st.columns(3)

        # Critical Routes Chart
    with col1:
        st.markdown("### 🔴 Critical Routes")
        if not critical_routes.empty:
            fig1 = px.bar(
                    critical_routes,
            x='route_name',
            y='route_delay_pct',
            color='route_delay_pct',
            color_continuous_scale='Reds',
                    title="Top Critical Routes",
                    labels={"route_delay_pct": "Delay %", "route_name": "Route"}
                )
            fig1.update_layout(xaxis_tickangle=-45, yaxis=dict(range=[0, 100]), showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.write("No critical routes found.")

    # Monitor Routes Chart
    with col2:
        st.markdown("### 🟠 Monitor Routes")
        if not monitor_routes.empty:
            fig2 = px.bar(
                monitor_routes,
                x='route_name',
                y='route_delay_pct',
                color='route_delay_pct',
                color_continuous_scale='Oranges',
                title="Top Monitor Routes",
                labels={"route_delay_pct": "Delay %", "route_name": "Route"}
            )
            fig2.update_layout(xaxis_tickangle=-45, yaxis=dict(range=[0, 100]), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.write("No monitor routes found.")

    # Healthy Routes Chart
    with col3:
        st.markdown("### 🟢 Healthy Routes")
        if not healthy_routes.empty:
            fig3 = px.bar(
                healthy_routes,
                x='route_name',
                y='route_delay_pct',
                color='route_delay_pct',
                color_continuous_scale='Greens',
                title="Top Healthy Routes",
                labels={"route_delay_pct": "Delay %", "route_name": "Route"}
            )
            fig3.update_layout(xaxis_tickangle=-45, yaxis=dict(range=[0, 100]), showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.write("No healthy routes found.")

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