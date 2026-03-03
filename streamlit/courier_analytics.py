import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db import run_query
from queries import *
from components import kpi_card
import pandas as pd

def app(run_query):
    st.header("🛵🚚 Courier Performance")
    courier_performance_df=run_query(courier_performance_query)
    
    # =============================
    # SHIPMENTS VS ON_TIME_DELIVERY
    # =============================
    # Create combined chart: Bar for shipments, line for on-time %
    fig = go.Figure()

    # Bar: Shipments handled
    fig.add_trace(go.Bar(
        x=courier_performance_df['courier_name'],
        y=courier_performance_df['total_shipments'],
        name='Shipments Handled',
        marker_color='skyblue',
        text=courier_performance_df['total_shipments'],
        textposition='auto'
    ))

    # Line: On-time delivery %
    fig.add_trace(go.Scatter(
        x=courier_performance_df['courier_name'],
        y=courier_performance_df['on_time_pct'],
        name='On-Time Delivery %',
        mode='lines+markers+text',
        text=courier_performance_df['on_time_pct'].apply(lambda x: f'{x:.1f}%'),
        textposition='top center',
        marker=dict(color='green', size=10),
        yaxis='y2'
    ))

    # Layout: secondary y-axis for on-time %
    fig.update_layout(
        title="📦 Courier Performance: Shipments vs On-Time Delivery",
        xaxis_title="Courier",
        yaxis=dict(title="Total Shipments"),
        yaxis2=dict(title="On-Time Delivery %", overlaying='y', side='right', range=[0,100]),
        legend=dict(x=0.75, y=1.1),
        template='plotly_white',
        barmode='group',
        hovermode='x'
    )
    fig.update_traces(text=None)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    
    # ==============================
    # SHIPMENT COUNT VS VEHICLE TYPE
    # ==============================
    st.subheader("🚛 Shipment Count vs Vehicle Type")
    vehicle_df=run_query(vehicle_query)
    fig = px.bar(
        vehicle_df,
        x='vehicle_type',
        y='shipments_handled',
        color='on_time_pct',            # optional: color by performance
        hover_data=['avg_delivery_hours', 'on_time_pct'],
        title='Shipment Count vs Vehicle Type',
        labels={'shipments_handled':'Shipments Handled','vehicle_type':'Vehicle Type'}
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.subheader("📋 Shipment Count vs Vehicle Type")
    st.dataframe(
        vehicle_df[['vehicle_type','shipments_handled','avg_delivery_hours','on_time_pct']],
        use_container_width=True
    )