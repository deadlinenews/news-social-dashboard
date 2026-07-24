import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

st.set_page_config(page_title="Social Media Dashboard", layout="wide")

# Custom CSS for modern card layout
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #4f46e5;
        margin-bottom: 15px;
    }
    .metric-title { font-size: 14px; color: #9ca3af; font-weight: 600; }
    .metric-value { font-size: 28px; font-weight: 700; color: #ffffff; }
    .platform-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_data(ttl=60)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('daily_stats').select('*').execute()
    return pd.DataFrame(response.data)

df = load_data()

st.title("⚡ Social Media Analytics Dashboard")
st.caption("Live metrics for **Deadline** & **The Edinburgh Reporter**")

if df.empty:
    st.warning("No data found in Supabase. Run collector.py first!")
else:
    # Filter to only active target outlets
    df = df[df['outlet_name'].isin(['Deadline', 'The Edinburgh Reporter'])]

    # Top Macro Overview
    st.markdown("### Executive Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">TOTAL AUDIENCE</div><div class="metric-value">{df["followers"].sum():,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">TOTAL ENGAGEMENTS</div><div class="metric-value">{df["likes"].sum():,}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">POSTS TRACKED</div><div class="metric-value">{df["posts_count"].sum():,}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">AVG ENGAGEMENT RATE</div><div class="metric-value">{df["engagement_rate"].mean():.2f}%</div></div>', unsafe_allow_html=True)

    # Tabs per Outlet & Overview
    tab_overview, tab_deadline, tab_edinburgh = st.tabs(["📊 Cross-Outlet Comparison", "🔴 Deadline News", "🔵 The Edinburgh Reporter"])

    with tab_overview:
        st.subheader("Platform Audience Breakdown")
        fig_bar = px.bar(
            df, 
            x="platform", 
            y="followers", 
            color="outlet_name",
            barmode="group",
            text_auto='.2s',
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Engagement Rate (%) by Platform")
        fig_er = px.bar(
            df, 
            x="platform", 
            y="engagement_rate", 
            color="outlet_name",
            barmode="group",
            text_auto='.2f',
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig_er, use_container_width=True)

    # Helper function to render outlet specific cards
    def render_outlet_view(outlet_name):
        outlet_df = df[df['outlet_name'] == outlet_name]
        st.subheader(f"{outlet_name} Channel Cards")
        
        cols = st.columns(len(outlet_df))
        for idx, (_, row) in enumerate(outlet_df.iterrows()):
            with cols[idx]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{row['platform'].upper()}</div>
                    <div class="metric-value">{row['followers']:,}</div>
                    <p style="color:#9ca3af; margin: 5px 0 0 0;">Likes: <b>{row['likes']:,}</b> | ER: <b>{row['engagement_rate']}%</b></p>
                </div>
                """, unsafe_allow_html=True)

        st.subheader("Detailed Breakdown")
        st.dataframe(
            outlet_df[['platform', 'followers', 'likes', 'posts_count', 'engagement_rate']], 
            use_container_width=True, 
            hide_index=True
        )

    with tab_deadline:
        render_outlet_view("Deadline")

    with tab_edinburgh:
        render_outlet_view("The Edinburgh Reporter")