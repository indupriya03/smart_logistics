# db.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text


# ===============================
# DATABASE CONNECTION
# ===============================
@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+mysqlconnector://root:root@localhost/logistics",
        pool_pre_ping=True  # auto-reconnects, replaces your conn.ping() logic
    )

def run_query(query, params=None):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)
            return df
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()