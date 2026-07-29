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

# FIXED CSS: Explicitly dark text (#2d3748 / #718096) for all sub-card titles and values
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
        color: #718096 !important; 
        font-weight: 600; 
        margin-bottom: 5px; 
    }
    .metric-value { 
        font-size: 28px; 
        font-weight: 800; 
        color: #1a202c !important; 
    }
    .sub-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #6b46c1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .sub-card h4 {
        color: #718096 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        margin-bottom: 8px !important;
        font-weight: 600 !important;
    }
    .sub-card h2 {
        font-size: 32px !important;
        font-weight: 800 !important;
        margin: 0 !important;
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

# -----------------------------------------------------------------------------
# TOP SUMMARY METRICS
# -----------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

if not filtered_df.empty and "record_date" in filtered_df.columns and "outlet_name" in filtered_df.columns and "platform" in filtered_df.columns:
    summary_df = filtered_df.sort_values("record_date", ascending=False).groupby(["outlet_name", "platform"]).first().reset_index()
else:
    summary_df = filtered_df.copy()

total_followers = int(summary_df["followers"].sum()) if not summary_df.empty and "followers" in summary_df.columns else 0
total_posts = int(summary_df["posts"].sum()) if not summary_df.empty and "posts" in summary_df.columns else 0
total_likes = int(summary_df["likes"].sum()) if not summary_df.empty and "likes" in summary_df.columns else 0
total_shares = int(summary_df["shares"].sum()) if not summary_df.empty and "shares" in summary_df.columns else 0
total_comments = int(summary_df["comments"].sum()) if not summary_df.empty and "comments" in summary_df.columns else 0

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

# -----------------------------------------------------------------------------
# TABBED SECTIONS
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Analytics Overview", "📑 Raw Metric Cards", "📈 Timeline Trends"])

with tab1:
    if selected_platform == "All Platforms":
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Follower Distribution by Platform")
            if not summary_df.empty and "followers" in summary_df.columns and "platform" in summary_df.columns:
                chart_df = summary_df.groupby(["platform", "outlet_name"], as_index=False)["followers"].sum()
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
            if not summary_df.empty and "likes" in summary_df.columns and "platform" in summary_df.columns:
                pie_df = summary_df.groupby("platform", as_index=False)["likes"].sum()
                
                # CLEANER PIE CHART: Places labels outside with clear callout lines and hides microscopic zero text
                fig_pie = go.Figure(data=[go.Pie(
                    labels=pie_df["platform"],
                    values=pie_df["likes"],
                    hole=0.3,
                    textinfo="label+percent",
                    textposition="outside",
                    marker=dict(colors=["#6B46C1", "#DD6B20", "#319795", "#805AD5", "#ED8936"])
                )])
                
                fig_pie.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#2D3748"),
                    showlegend=True,
                    margin=dict(t=30, b=30, l=30, r=30)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No engagement metrics available to plot.")
    else:
        st.subheader(f"In-Depth {selected_platform} Metrics")
        
        avg_likes_per_post = round(total_likes / total_posts, 1) if total_posts > 0 else 0
        est_er = round((total_likes / total_followers) * 100, 2) if total_followers > 0 else 0.0
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.markdown(f'<div class="sub-card"><h4>Avg Likes per Post</h4><h2 style="color:#6b46c1;">{avg_likes_per_post:,}</h2></div>', unsafe_allow_html=True)
        with col_p2:
            st.markdown(f'<div class="sub-card"><h4>Engagement Rate</h4><h2 style="color:#dd6b20;">{est_er}%</h2></div>', unsafe_allow_html=True)
        with col_p3:
            st.markdown(f'<div class="sub-card"><h4>Account Audience Reach</h4><h2 style="color:#319795;">{total_followers:,}</h2></div>', unsafe_allow_html=True)

with tab2:
    st.subheader("Raw Metric Breakdown (Latest Snapshots Only)")
    st.markdown("Detailed view of the most recent snapshot for each outlet and platform combination.")
    
    if not filtered_df.empty:
        if "record_date" in filtered_df.columns and "outlet_name" in filtered_df.columns and "platform" in filtered_df.columns:
            latest_cards_df = filtered_df.sort_values("record_date", ascending=False).groupby(["outlet_name", "platform"]).first().reset_index()
        else:
            latest_cards_df = filtered_df.copy()

        for idx, row in latest_cards_df.iterrows():
            outlet = row.get("outlet_name", "Unknown Outlet")
            plat = row.get("platform", "Unknown Platform")
            rec_date = row.get("record_date", "N/A")
            f_count = int(row.get("followers", 0))
            p_count = int(row.get("posts", 0))
            l_count = int(row.get("likes", 0))
            s_count = int(row.get("shares", 0))
            c_count = int(row.get("comments", 0))
            er_rate = row.get("engagement_rate", 0.0)

            st.markdown(f"""
            <div style="background: #ffffff; border-radius: 10px; padding: 18px; margin-bottom: 12px; border-left: 5px solid #6b46c1; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 16px; color: #5a2789;">{outlet} — {plat}</strong>
                    <span style="font-size: 12px; color: #718096;">Latest Snapshot: {rec_date}</span>
                </div>
                <div style="display: flex; gap: 24px; margin-top: 12px; flex-wrap: wrap;">
                    <div><span style="font-size: 11px; color: #718096; text-transform: uppercase;">Followers</span><br/><strong style="font-size: 16px; color: #2d3748;">{f_count:,}</strong></div>
                    <div><span style="font-size: 11px; color: #718096; text-transform: uppercase;">Posts</span><br/><strong style="font-size: 16px; color: #2d3748;">{p_count:,}</strong></div>
                    <div><span style="font-size: 11px; color: #718096; text-transform: uppercase;">Likes</span><br/><strong style="font-size: 16px; color: #2d3748;">{l_count:,}</strong></div>
                    <div><span style="font-size: 11px; color: #718096; text-transform: uppercase;">Shares</span><br/><strong style="font-size: 16px; color: #2d3748;">{s_count:,}</strong></div>
                    <div><span style="font-size: 11px; color: #718096; text-transform: uppercase;">Comments</span><br/><strong style="font-size: 16px; color: #2d3748;">{c_count:,}</strong></div>
                    <div><span style="font-size: 11px; color: #718096; text-transform: uppercase;">Engagement Rate</span><br/><strong style="font-size: 16px; color: #dd6b20;">{er_rate}%</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
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
