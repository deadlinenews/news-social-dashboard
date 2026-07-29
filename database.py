import os
import pandas as pd
from supabase import create_client

# Retrieve Supabase credentials safely from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hwmccakzfrnuwxzdfxef.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3bWNjYWt6ZnJudXd4emRmeGVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ4ODE5ODUsImV4cCI6MjEwMDQ1Nzk4NX0.J-k7CPID1jFLoFkhWqXnxGTKS_hG-egKvwqbyVBi_ZM")

def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_latest_metrics():
    """Fetches the latest snapshot metrics from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('daily_stats').select('*').order('record_date', desc=True).execute()
        
        if not response.data:
            return pd.DataFrame()
            
        df = pd.DataFrame(response.data)
        
        # Standardise column names for app.py
        if 'posts_count' in df.columns and 'posts' not in df.columns:
            df['posts'] = df['posts_count']
        if 'likes_count' in df.columns and 'likes' not in df.columns:
            df['likes'] = df['likes_count']
        if 'shares_count' in df.columns and 'shares' not in df.columns:
            df['shares'] = df['shares_count']
        elif 'shares' not in df.columns:
            df['shares'] = 0
        if 'comments_count' in df.columns and 'comments' not in df.columns:
            df['comments'] = df['comments_count']
        elif 'comments' not in df.columns:
            df['comments'] = 0

        # Keep only the latest entry per outlet & platform combination
        latest_df = df.sort_values('record_date', ascending=False).groupby(['outlet_name', 'platform']).first().reset_index()
        return latest_df
    except Exception as e:
        print(f"Error fetching latest metrics: {e}")
        return pd.DataFrame()

def get_history():
    """Fetches full historical timeline metrics from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('daily_stats').select('*').order('record_date', asc=True).execute()
        
        if not response.data:
            return pd.DataFrame()
            
        df = pd.DataFrame(response.data)
        if 'record_date' in df.columns:
            df['snapshot_date'] = df['record_date']
        return df
    except Exception as e:
        print(f"Error fetching history: {e}")
        return pd.DataFrame()
