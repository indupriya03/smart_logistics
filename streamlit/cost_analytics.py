import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db import run_query
from queries import *
from components import kpi_card
import pandas as pd

def app(run_query):
    st.header("💰⚙️ Cost & Efficiency Analytics")
    # ===========================
    #  Key Performance Indicators
    # ===========================
    col1, col2, col3, col4= st.columns(4)
    cost_metrics_df = run_query(cost_metrics_query)
    total_cost = cost_metrics_df['total_cost'].sum()
    total_shipments = cost_metrics_df['total_shipments'].sum()

    avg_cost_per_shipment = total_cost / total_shipments

    avg_cost_per_km = (
        cost_metrics_df['total_cost'].sum() /
        (cost_metrics_df['distance_km'] * cost_metrics_df['total_shipments']).sum()
    )

    most_expensive_route = cost_metrics_df.loc[cost_metrics_df['total_cost'].idxmax()]
    with col1:
        kpi_card("💸 Total Network Cost", f"${total_cost:,.2f}")
    with col2:
        kpi_card("📦 Avg Cost per Shipment", f"${avg_cost_per_shipment:,.2f}")
    with col3:
        kpi_card("📏 Avg Cost per KM", f"${avg_cost_per_km:,.2f}")
    with col4:
        kpi_card("🔥 Most Expensive Route", most_expensive_route['route_name'])

    st.markdown("---")
    # ================
    # COSTS BREAKDOWN
    # ================
    st.subheader("💰 Cost Breakdown Chart ")

    cost_df=run_query(cost_query)


    # Route-level metrics
    route_metrics = cost_df.groupby(['route_key','route_name','distance_km']).agg(
        total_cost=('total_cost','sum'),
        fuel=('fuel','sum'),
        labor=('labor','sum'),
        misc=('misc','sum'),
        total_shipments=('total_shipments','sum')
    ).reset_index()
    route_metrics['total_cost'] = route_metrics['fuel'] + route_metrics['labor'] + route_metrics['misc']
    route_metrics['avg_cost_per_shipment'] = route_metrics['total_cost'] / route_metrics['total_shipments']
    route_metrics['cost_per_km'] = route_metrics['total_cost'] / route_metrics['distance_km']

        # Network-level metrics
    network_total = pd.DataFrame({
        'fuel': [cost_df['fuel'].sum()],
        'labor': [cost_df['labor'].sum()],
        'misc': [cost_df['misc'].sum()]
    })
    network_total['total_cost'] = network_total.sum(axis=1)[0]

    # Top 5 high-cost shipments
    cost_df['total_cost'] = cost_df['fuel'] + cost_df['labor'] + cost_df['misc']
    top5_shipments = cost_df.sort_values('total_cost', ascending=False).head(5)

    fig_donut = px.pie(
        network_total.melt(value_vars=['fuel','labor','misc'], var_name='Cost Type', value_name='Cost'),
        values='Cost', names='Cost Type',
        hole=0.5,
        color='Cost Type',
        color_discrete_map={'fuel':'#1f77b4','labor':'#ff7f0e','misc':'#2ca02c'}
    )
    fig_donut.update_layout(
        title="Cost Breakdown",
        annotations=[dict(text=f"${network_total['total_cost'].iloc[0]:,.0f}", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # =========================
    # Top 5 High-Cost Shipments
    # =========================
    st.subheader("🚨 Top 5 High-Cost Shipments")
    st.dataframe(
        top5_shipments[['shipment_id','route_name','distance_km','fuel','labor','misc','total_cost']]
        .style.format({
            'fuel_cost':'${:.2f}',
            'labor_cost':'${:.2f}',
            'misc_cost':'${:.2f}',
            'total_cost':'${:.2f}',
            'distance_km':'{:.2f} km'
        }),
        use_container_width=True
    )

    st.markdown("---")

    # ========================
    # Cost per Route Bar Chart
    # ========================
    top_n = 10  # show only top 10 routes by total cost
    top_cost_routes = route_metrics.sort_values('total_cost', ascending=False).head(top_n)
    
    fig_route = px.bar(
        top_cost_routes,
        x='route_name',
        y='total_cost',
        color='total_cost',
        color_continuous_scale='Reds',
        title="Total Cost per Route"
    )
    fig_route.update_layout(yaxis_title="Total Cost ($)", xaxis_title="Route", coloraxis_showscale=False)
    st.plotly_chart(fig_route, use_container_width=True)