import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import fetch_latest_metrics, fetch_timeline_data

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS (PURPLE & ORANGE LIGHT THEME)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Social Media Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Background & Base Typography */
    .main {
        background-color: #f8f9fa;
        color: #2d3748;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #5a2789 !important;
        font-weight: 700 !important;
    }
    
    /* Custom Metric Cards */
    .metric-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.08);
        border-top: 4px solid #6b46c1;
        margin-bottom: 15px;
    }
    .metric-card-orange {
        border-top: 4px solid #dd6b20;
    }
    .metric-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #718096;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #1a202c;
    }
    .metric-subtext {
        font-size: 12px;
        color: #38a169;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Streamlit Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #ffffff;
        border-radius: 8px 8px 0px 0px;
        color: #4a5568;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6b46c1 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA LOADING & SIDEBAR FILTERS
# -----------------------------------------------------------------------------
df_latest = fetch_latest_metrics()
df_timeline = fetch_timeline_data()

st.sidebar.image("https://img.icons8.com/fluent/96/000000/analytics.png", width=60)
st.sidebar.title("Dashboard Controls")

# Outlet Filter
outlets = ["All Newspapers"] + list(df_latest["outlet_name"].unique()) if not df_latest.empty else ["All Newspapers"]
selected_outlet = st.sidebar.selectbox("Select Newspaper", outlets)

# Platform Filter
platforms = ["All Platforms"] + list(df_latest["platform"].unique()) if not df_latest.empty else ["All Platforms"]
selected_platform = st.sidebar.selectbox("Select Platform", platforms)

# Filter Dataframe
filtered_df = df_latest.copy()
if selected_outlet != "All Newspapers":
    filtered_df = filtered_df[filtered_df["outlet_name"] == selected_outlet]
if selected_platform != "All Platforms":
    filtered_df = filtered_df[filtered_df["platform"] == selected_platform]

# -----------------------------------------------------------------------------
# 3. MAIN DASHBOARD HEADER
# -----------------------------------------------------------------------------
st.title("Social Media Performance Dashboard")
st.markdown(f"**Viewing:** `{selected_outlet}` | **Platform:** `{selected_platform}`")
st.divider()

# -----------------------------------------------------------------------------
# 4. TOP SUMMARY METRIC CARDS
# -----------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

total_followers = filtered_df["followers"].sum() if "followers" in filtered_df.columns else 0
total_posts = filtered_df["posts"].sum() if "posts" in filtered_df.columns else 0
total_likes = filtered_df["likes"].sum() if "likes" in filtered_df.columns else 0
total_shares = filtered_df["shares"].sum() if "shares" in filtered_df.columns else 0
total_comments = filtered_df["comments"].sum() if "comments" in filtered_df.columns else 0

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Followers</div>
        <div class="metric-value">{total_followers:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card metric-card-orange">
        <div class="metric-title">Total Posts</div>
        <div class="metric-value">{total_posts:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Likes</div>
        <div class="metric-value">{total_likes:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card metric-card-orange">
        <div class="metric-title">Total Shares / Retweets</div>
        <div class="metric-value">{total_shares:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Comments</div>
        <div class="metric-value">{total_comments:,}</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. CHARTS AND DETAILED BREAKDOWNS
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Visual Analytics", "📑 Raw Engagement Data", "📈 Timeline Trends"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Follower Distribution by Platform")
        if not filtered_df.empty:
            fig_bar = px.bar(
                filtered_df,
                x="platform",
                y="followers",
                color="outlet_name",
                barmode="group",
                color_discrete_sequence=["#6B46C1", "#DD6B20", "#319795", "#D69E2E"],
                text_auto='.2s'
            )
            fig_bar.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#2D3748"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#E2E8F0")
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with col_chart2:
        st.subheader("Engagement Share (Likes & Comments)")
        if not filtered_df.empty and "likes" in filtered_df.columns:
            fig_pie = px.pie(
                filtered_df,
                names="platform",
                values="likes",
                color_discrete_sequence=["#6B46C1", "#805AD5", "#9F7AEA", "#DD6B20", "#ED8936"]
            )
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#2D3748")
            )
            st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Raw Metrics Breakdown")
    st.markdown("Detailed breakdown of posts, reach, likes, shares, and comments across all outlets.")
    
    # Display raw data table with formatted numbers
    display_cols = [col for col in ["outlet_name", "platform", "followers", "posts", "likes", "shares", "comments"] if col in filtered_df.columns]
    st.dataframe(
        filtered_df[display_cols].style.format({
            "followers": "{:,}",
            "posts": "{:,}",
            "likes": "{:,}",
            "shares": "{:,}",
            "comments": "{:,}"
        }),
        use_container_width=True
    )

with tab3:
    st.subheader("Performance Over Time")
    if not df_timeline.empty:
        # Filter timeline dataset based on user selections
        timeline_filtered = df_timeline.copy()
        if selected_outlet != "All Newspapers":
            timeline_filtered = timeline_filtered[timeline_filtered["outlet_name"] == selected_outlet]
        if selected_platform != "All Platforms":
            timeline_filtered = timeline_filtered[timeline_filtered["platform"] == selected_platform]
            
        fig_line = px.line(
            timeline_filtered,
            x="snapshot_date",
            y="followers",
            color="platform",
            line_group="outlet_name",
            color_discrete_sequence=["#6B46C1", "#DD6B20", "#319795", "#3182CE"]
        )
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#2D3748"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0")
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No historical timeline data available yet.")
