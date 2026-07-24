import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from ai_engine import generate_ai_insights

st.set_page_config(page_title="News Outlet Social Dashboard", layout="wide")

st.title("📰 News Outlet Social Media Tracker")
st.markdown("Tracking **Deadline**, **The Edinburgh Reporter**, and **The Glasgow Reporter** across 6 platforms.")

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Missing cloud configuration secrets. Please configure secrets in Streamlit Cloud.")
    st.stop()

@st.cache_data(ttl=600)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('daily_stats').select('*').execute()
    return pd.DataFrame(response.data)

df = load_data()

if df.empty:
    st.warning("Database is empty. Waiting for daily Apify run to populate data.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Profiles Monitored", len(df[['outlet_name', 'platform']].drop_duplicates()))
    col2.metric("Total Combined Reach", f"{df['followers'].sum():,}")
    col3.metric("Average Engagement Rate", f"{df['engagement_rate'].mean():.2f}%")

    st.markdown("---")

    st.subheader("🤖 AI Performance Insights")
    if st.button("Generate Fresh Analysis"):
        with st.spinner("Analyzing cross-channel metrics..."):
            summary = generate_ai_insights(OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY)
            st.info(summary)

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Follower Distribution by Outlet")
        fig_followers = px.bar(
            df, 
            x="outlet_name", 
            y="followers", 
            color="platform", 
            barmode="group"
        )
        st.plotly_chart(fig_followers, use_container_width=True)

    with chart_col2:
        st.subheader("Engagement Rate (%) Comparison")
        fig_er = px.bar(
            df, 
            x="platform", 
            y="engagement_rate", 
            color="outlet_name", 
            barmode="group"
        )
        st.plotly_chart(fig_er, use_container_width=True)

    with st.expander("View Raw Database Entries"):
        st.dataframe(df.sort_values(by="record_date", ascending=False), use_container_width=True)
