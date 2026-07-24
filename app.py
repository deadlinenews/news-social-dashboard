import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client

# Streamlit Page Config
st.set_page_config(page_title="News Social Dashboard", layout="wide")

# Supabase Credentials from Streamlit Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_data(ttl=60)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('daily_stats').select('*').execute()
    df = pd.DataFrame(response.data)
    
    if not df.empty:
        # Standardize platform names
        platform_map = {
            'twitter': 'X',
            'x': 'X',
            'facebook': 'Facebook',
            'instagram': 'Instagram',
            'linkedin': 'LinkedIn',
            'threads': 'Threads'
        }
        df['platform'] = df['platform'].astype(str).str.lower().map(lambda p: platform_map.get(p, p.title()))
        
        # Format date column
        df['record_date'] = pd.to_datetime(df['record_date'])
        
        # Ensure numeric types
        df['followers'] = pd.to_numeric(df['followers'], errors='coerce').fillna(0)
        df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
        df['posts_count'] = pd.to_numeric(df['posts_count'], errors='coerce').fillna(1)
        
        # Recalculate ER dynamically if current database ER is 0 but likes exist
        df['engagement_rate'] = df.apply(
            lambda row: round((row['likes'] / (row['followers'] * row['posts_count'])) * 100, 2)
            if row['followers'] > 0 and row['likes'] > 0 else row['engagement_rate'],
            axis=1
        )

    return df

st.title("📰 News Social Media Dashboard")

df = load_data()

if df.empty:
    st.warning("No data found in Supabase database.")
else:
    # Create Tabs
    tab_overview, tab_timeline = st.tabs(["📊 Overview", "📈 Timeline Comparison"])

    # ---------------------------------------------------------
    # TAB 1: OVERVIEW (Latest Snapshot)
    # ---------------------------------------------------------
    with tab_overview:
        # Get latest day's data
        latest_date = df['record_date'].max()
        df_latest = df[df['record_date'] == latest_date]
        
        # Deduplicate latest day
        df_latest = df_latest.groupby(['outlet_name', 'platform'], as_index=False).last()

        # Top KPIs
        total_followers = int(df_latest['followers'].sum())
        avg_er = round(df_latest['engagement_rate'].mean(), 2)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Snapshot Date", latest_date.strftime('%Y-%m-%d'))
        col2.metric("Total Followers (All Outlets)", f"{total_followers:,}")
        col3.metric("Avg Engagement Rate", f"{avg_er}%")

        st.divider()

        # Overview Charts
        fig_followers = px.bar(
            df_latest,
            x="platform",
            y="followers",
            color="outlet_name",
            barmode="group",
            text_auto='.2s',
            title="Audience Breakdown by Platform"
        )
        st.plotly_chart(fig_followers, use_container_width=True)

        fig_er = px.bar(
            df_latest,
            x="platform",
            y="engagement_rate",
            color="outlet_name",
            barmode="group",
            title="Engagement Rate (%) by Platform"
        )
        st.plotly_chart(fig_er, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 2: TIMELINE COMPARISON
    # ---------------------------------------------------------
    with tab_timeline:
        st.subheader("📈 Historical Growth & Comparison")

        # Preset & Custom Filters
        col_preset, col_outlet, col_metric = st.columns(3)
        
        with col_preset:
            time_preset = st.selectbox(
                "Timeframe Range",
                ["Last 30 Days", "Last 90 Days", "Custom Date Range"]
            )

        max_date = df['record_date'].max().date()
        min_db_date = df['record_date'].min().date()

        if time_preset == "Last 30 Days":
            start_date = max_date - timedelta(days=30)
            end_date = max_date
        elif time_preset == "Last 90 Days":
            start_date = max_date - timedelta(days=90)
            end_date = max_date
        else:
            # Custom Date Range picker
            date_range = st.date_input(
                "Select Date Range",
                value=(min_db_date, max_date),
                min_value=min_db_date,
                max_value=max_date
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date, end_date = min_db_date, max_date

        with col_outlet:
            outlets = ["All Outlets"] + list(df['outlet_name'].unique())
            selected_outlet = st.selectbox("Filter Outlet", outlets)

        with col_metric:
            selected_metric = st.selectbox("Select Metric", ["followers", "engagement_rate", "likes"])

        # Filter dataset based on inputs
        df_filtered = df[(df['record_date'].dt.date >= start_date) & (df['record_date'].dt.date <= end_date)]

        if selected_outlet != "All Outlets":
            df_filtered = df_filtered[df_filtered['outlet_name'] == selected_outlet]

        if df_filtered.empty:
            st.info("No historical data available for the selected filters.")
        else:
            # Line Chart over time
            metric_title = selected_metric.replace('_', ' ').title()
            
            fig_timeline = px.line(
                df_filtered,
                x="record_date",
                y=selected_metric,
                color="outlet_name",
                line_dash="platform",
                markers=True,
                title=f"{metric_title} Trend ({start_date} to {end_date})",
                labels={"record_date": "Date", selected_metric: metric_title}
            )
            fig_timeline.update_layout(hovermode="x unified")
            st.plotly_chart(fig_timeline, use_container_width=True)

            # Summary Table
            st.markdown("### 📊 Raw Data Log")
            st.dataframe(
                df_filtered[['record_date', 'outlet_name', 'platform', 'followers', 'likes', 'engagement_rate']]
                .sort_values('record_date', ascending=False),
                use_container_width=True
            )
