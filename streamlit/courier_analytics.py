import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from db import run_query
from queries import *
from components import kpi_card
import pandas as pd

def app(run_query):
    st.header("🛵🚚 Courier Performance")
    courier_performance_df=run_query(courier_performance_query)
    
    # # =============================
    # # SHIPMENTS VS ON_TIME_DELIVERY
    # # =============================

    fig = px.scatter(
        courier_performance_df,
        x="total_shipments",
        y="on_time_pct",
        hover_name="courier_name",
        hover_data={"rating": True},
        labels={
            "total_shipments": "Total Shipments",
            "on_time_pct": "On-Time Delivery (%)",
            "rating" : "Rating"
        },
        title="Courier Performance Analysis"
    )

    fig.update_traces(textposition="top center")

    st.plotly_chart(fig, use_container_width=True)
    # ==============================
    # COURIER CANCELLATION ANALYSIS
    # ==============================
    st.subheader("Courier Cancellation Analysis")
    st.markdown("### Cancellation Rate by Courier")
    cancel_courier_df = run_query(cancel_by_courier_query)
    fig = px.bar(
        cancel_courier_df,
        x="courier_name",
        y="cancellation_rate_pct",
        color="vehicle_type",  # optional
        hover_data=["rating", "total_shipments", "cancelled_shipments"],
        labels={"cancellation_rate_pct": "Cancellation Rate (%)",
                "courier_name": "Courier Name",
                "vehicle_type": "Vehicle Type"
        },
        title="Courier Cancellation Rate"
    )

    fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0, cancel_courier_df['cancellation_rate_pct'].max() + 5])

    st.plotly_chart(fig, use_container_width=True)
    
    # ==============================
    # SHIPMENT COUNT VS VEHICLE TYPE
    # ==============================
    st.subheader("🚛 Vehicle Type Distribution")
    vehicle_df=run_query(vehicle_query)
    col1, col2 = st.columns(2)
    with col1:
        fig= px.bar(
            vehicle_df,
            x='vehicle_type',
            y='shipments_handled',
            color='on_time_pct',            # optional: color by performance
            hover_data=['avg_delivery_hours', 'on_time_pct'],
            title='Shipment Count vs Vehicle Type',
            labels={'shipments_handled':'Shipments Handled','vehicle_type':'Vehicle Type'}
        )

        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig_pie = px.pie(
            vehicle_df,
            names='vehicle_type',
            values='shipments_handled',
            title='Vehicle Type Share',
            color='vehicle_type'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("---")
    st.subheader("📋 Shipment Count vs Vehicle Type")
    st.dataframe(
        vehicle_df[['vehicle_type','shipments_handled','avg_delivery_hours','on_time_pct']],
        use_container_width=True
    )