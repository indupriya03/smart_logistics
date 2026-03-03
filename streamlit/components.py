import streamlit as st
# ===============================
# KPI CARD DESIGN
# ===============================
def kpi_card(title, value, delta=None, color="#1f77b4"):
    st.markdown(f"""
    <div style="
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        white-space: nowrap;
        overflow: hidden;
        flex: 1;
        min-width: 0;
        min-height: 180px;
        min-width: 0;
    ">
        <h4 style="margin:0; color:#555555; font-size:clamp(12px,1.2vw,16px);">{title}</h4>
        <h2 style="margin:5px 0; color:{color}; font-size:clamp(12px,1.5vw,22px);">{value}</h2>
        {f'<p style="margin:0; color:green;">{delta}</p>' if delta else ""}
    </div>
    """, unsafe_allow_html=True)