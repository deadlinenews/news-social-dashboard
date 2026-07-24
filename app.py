import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

st.set_page_config(page_title="Social Media Tracker", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_data(ttl=60)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('daily_stats').select('*').execute()
    return pd.DataFrame(response.data)

df = load_data()

st.title("📰 News Outlet Social Media Tracker")
st.markdown("Tracking **Deadline** and **The Edinburgh Reporter** across active channels.")

if df.empty:
    st.warning("Database is empty.")
else:
    # Top Overview Metric Cards (Like modern dashboard cards)
    st.subheader("Overview")
    total_followers = df['followers'].sum()
    total_posts = df['posts_count'].sum()
    avg_er = df['engagement_rate'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Followers Across Channels", f"{total_followers:,}")
    col2.metric("Total Posts Logged", f"{total_posts:,}")
    col3.metric("Avg. Engagement Rate", f"{avg_er:.2f}%")

    st.divider()

    # Visualizations (Side-by-Side Charts)
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Follower Count by Platform & Outlet")
        fig_followers = px.bar(
            df, 
            x="platform", 
            y="followers", 
            color="outlet_name", 
            barmode="group",
            text_auto='.2s',
            template="plotly_dark"
        )
        st.plotly_chart(fig_followers, use_container_width=True)

    with col_right:
        st.subheader("Engagement Rate (%) by Platform")
        fig_er = px.line(
            df, 
            x="platform", 
            y="engagement_rate", 
            color="outlet_name", 
            markers=True,
            template="plotly_dark"
        )
        st.plotly_chart(fig_er, use_container_width=True)