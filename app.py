import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

db_available = False
try:
    from database import get_latest_metrics, get_history
    db_available = True
except Exception as e:
    db_error = str(e)

st.set_page_config(
    page_title="Social Media Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { 
        background-color: #f8f9fa; 
        color: #2d3748; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
    }
    h1, h2, h3 { 
        color: #5a2789 !important; 
        font-weight: 700 !important; 
    }
    .metric-card { 
        background: #ffffff; 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); 
        border-top: 4px solid #6b46c1; 
        margin-bottom: 15px; 
    }
    .metric-card-orange { 
        border-top: 4px solid #dd6b20; 
    }
    .metric-title { 
        font-size: 13px; 
        text-transform: uppercase; 
        color: #718096; 
        font-weight: 600; 
        margin-bottom: 5px; 
    }
    .metric-value { 
        font-size: 28px; 
        font-weight: 800; 
        color: #1a202c; 
    }
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

def clean_data(df):
    if df.empty:
        return df
    df = df.copy()
    
    platform_map = {
        'twitter': 'X',
        'x': 'X',
        'facebook': 'Facebook',
        'instagram': 'Instagram',
        'linkedin': 'LinkedIn',
        'threads': 'Threads'
    }
    if 'platform' in df.columns:
        df['platform'] = df['platform'].astype(str).str.strip().str.lower().map(lambda x: platform_map.get(x, x.title()))
        
    return df

if db_available:
    try:
        df_latest = clean_data(get_latest_metrics())
        df_timeline = clean_data(get_history())
    except Exception as err:
        st.error(f"Error executing database functions: {err}")
        df_latest = pd.DataFrame()
        df_timeline = pd.DataFrame()
else:
    st.error(f"Failed to load database module: {db_error}")
    df_latest = pd.DataFrame()
    df_timeline = pd.DataFrame()

st.sidebar.title("Dashboard Controls")

outlets = ["All Newspapers"]
if not df_latest.empty and "outlet_name" in df_latest.columns:
    outlets += list(df_latest["outlet_name"].dropna().unique())
selected_outlet = st.sidebar.selectbox("Select Newspaper", outlets)

platforms = ["All Platforms"]
if not df_latest.empty and "platform" in df_latest.columns:
    platforms += list(df_latest["platform"].dropna().unique())
selected_platform = st.sidebar.selectbox("Select Platform", platforms)

filtered_df = df_latest.copy() if not df_latest.empty else pd.DataFrame()
if not filtered_df.empty:
    if selected_outlet != "All Newspapers" and "outlet_name" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["outlet_name"] == selected_outlet]
    if selected_platform != "All Platforms" and "platform" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["platform"] == selected_platform]

st.title("Social Media Performance Dashboard")
st.markdown(f"**Viewing:** `{selected_outlet}` | **Platform:** `{selected_platform}`")
st.divider()

col1, col2, col3, col4, col5 = st.columns(5)

total_followers = int(filtered_df["followers"].sum()) if not filtered_df.empty and "followers" in filtered_df.columns else 0
total_posts = int(filtered_df["posts"].sum()) if not filtered_df.empty and "posts" in filtered_df.columns else 0
total_likes = int(filtered_df["likes"].sum()) if not filtered_df.empty and "likes" in filtered_df.columns else 0
total_shares = int(filtered_df["shares"].sum()) if not filtered_df.empty and "shares" in filtered_df.columns else 0
total_comments = int(filtered_df["comments"].sum()) if not filtered_df.empty and "comments" in filtered_df.columns else 0

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Followers</div><div class="metric-value">{total_followers:,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card metric-card-orange"><div class="metric-title">Total Posts</div><div class="metric-value">{total_posts:,}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Likes</div><div class="metric-value">{total_likes:,}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card metric-card-orange"><div class="metric-title">Total Shares</div><div class="metric-value">{total_shares:,}</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Comments</div><div class="metric-value">{total_comments:,}</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Visual Analytics", "📑 Raw Engagement Data", "📈 Timeline Trends"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Follower Distribution by Platform")
        if not filtered_df.empty and "followers" in filtered_df.columns and "platform" in filtered_df.columns:
            chart_df = filtered_df.groupby(["platform", "outlet_name"], as_index=False)["followers"].sum()
            fig_bar = px.bar(
                chart_df,
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
        else:
            st.info("No follower metrics available to plot.")
            
    with col_chart2:
        st.subheader("Engagement Share (Likes)")
        if not filtered_df.empty and "likes" in filtered_df.columns and "platform" in filtered_df.columns:
            pie_df = filtered_df.groupby("platform", as_index=False)["likes"].sum()
            fig_pie = px.pie(
                pie_df,
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
        else:
            st.info("No engagement metrics available to plot.")

with tab2:
    st.subheader("Raw Metrics Breakdown")
    st.markdown("Detailed breakdown of posts, reach, likes, shares, and comments across all outlets.")
    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No raw data currently loaded.")

with tab3:
    st.subheader("Performance Over Time")
    if not df_timeline.empty and "snapshot_date" in df_timeline.columns:
        timeline_filtered = df_timeline.copy()
        if selected_outlet != "All Newspapers" and "outlet_name" in timeline_filtered.columns:
            timeline_filtered = timeline_filtered[timeline_filtered["outlet_name"] == selected_outlet]
        if selected_platform != "All Platforms" and "platform" in timeline_filtered.columns:
            timeline_filtered = timeline_filtered[timeline_filtered["platform"] == selected_platform]
            
        fig_line = px.line(
            timeline_filtered,
            x="snapshot_date",
            y="followers" if "followers" in timeline_filtered.columns else None,
            color="platform" if "platform" in timeline_filtered.columns else None,
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
        st.info("No historical timeline data recorded yet.")
