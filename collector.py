import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hwmccakzfrnuwxzdfxef.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3bWNjYWt6ZnJudXd4emRmeGVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ4ODE5ODUsImV4cCI6MjEwMDQ1Nzk4NX0.J-k7CPID1jFLoFkhWqXnxGTKS_hG-egKvwqbyVBi_ZM")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_metric(outlet, platform, followers, likes, posts_count):
    today = datetime.now().strftime('%Y-%m-%d')
    er = round((likes / (followers * posts_count)) * 100, 4) if followers > 0 and posts_count > 0 else 0.0
    
    payload = {
        "outlet_name": outlet,
        "platform": platform,
        "record_date": today,
        "followers": followers,
        "likes": likes,
        "posts_count": posts_count,
        "engagement_rate": er
    }
    
    supabase.table('daily_stats').insert(payload).execute()

def run_daily_collection():
    # Only the active platforms you track:
    sample_data = [
        # Deadline News: X, Facebook, Instagram, LinkedIn
        {"outlet": "Deadline", "platform": "X", "followers": 350000, "likes": 15000, "posts": 25},
        {"outlet": "Deadline", "platform": "Facebook", "followers": 180000, "likes": 5200, "posts": 12},
        {"outlet": "Deadline", "platform": "Instagram", "followers": 95000, "likes": 8400, "posts": 8},
        {"outlet": "Deadline", "platform": "LinkedIn", "followers": 42000, "likes": 1800, "posts": 5},

        # Edinburgh Reporter: X, Facebook, Instagram, Threads
        {"outlet": "The Edinburgh Reporter", "platform": "X", "followers": 45000, "likes": 2100, "posts": 10},
        {"outlet": "The Edinburgh Reporter", "platform": "Facebook", "followers": 38000, "likes": 1900, "posts": 6},
        {"outlet": "The Edinburgh Reporter", "platform": "Instagram", "followers": 18500, "likes": 1200, "posts": 4},
        {"outlet": "The Edinburgh Reporter", "platform": "Threads", "followers": 8200, "likes": 650, "posts": 3},
    ]
    
    for entry in sample_data:
        log_metric(entry["outlet"], entry["platform"], entry["followers"], entry["likes"], entry["posts"])

if __name__ == "__main__":
    run_daily_collection()
    print("Metrics logged to Supabase successfully!")