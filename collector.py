import os
from datetime import datetime
from supabase import create_client

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hwmccakzfrnuwxzdfxef.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3bWNjYWt6ZnJudXd4emRmeGVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ4ODE5ODUsImV4cCI6MjEwMDQ1Nzk4NX0.J-k7CPID1jFLoFkhWqXnxGTKS_hG-egKvwqbyVBi_ZM")

# Initialize Supabase Client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_metric(outlet, platform, followers, likes, posts_count):
    today = datetime.now().strftime('%Y-%m-%d')
    
    er = 0.0
    if followers > 0 and posts_count > 0:
        er = round((likes / (followers * posts_count)) * 100, 4)
        
    # Build payload to insert into Supabase
    payload = {
        "outlet_name": outlet,
        "platform": platform,
        "record_date": today,
        "followers": followers,
        "likes": likes,
        "posts_count": posts_count,
        "engagement_rate": er
    }
    
    # Insert record into 'daily_stats' table in Supabase
    response = supabase.table('daily_stats').insert(payload).execute()

def run_daily_collection():
    sample_data = [
        {"outlet": "Deadline", "platform": "X", "followers": 3500000, "likes": 15000, "posts": 25},
        {"outlet": "Deadline", "platform": "Bluesky", "followers": 120000, "likes": 4200, "posts": 10},
        {"outlet": "The Edinburgh Reporter", "platform": "Instagram", "followers": 18500, "likes": 1200, "posts": 4},
        {"outlet": "The Edinburgh Reporter", "platform": "Facebook", "followers": 45000, "likes": 2100, "posts": 6},
        {"outlet": "The Glasgow Reporter", "platform": "Threads", "followers": 8200, "likes": 650, "posts": 3},
        {"outlet": "The Glasgow Reporter", "platform": "LinkedIn", "followers": 11000, "likes": 410, "posts": 2},
    ]
    
    for entry in sample_data:
        log_metric(
            entry["outlet"], 
            entry["platform"], 
            entry["followers"], 
            entry["likes"], 
            entry["posts"]
        )

if __name__ == "__main__":
    run_daily_collection()
    print("Metrics logged to Supabase successfully!")