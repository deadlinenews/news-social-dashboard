import sqlite3
from datetime import datetime

def log_metric(outlet, platform, followers, likes, posts_count):
    today = datetime.now().strftime('%Y-%m-%d')
    
    er = 0.0
    if followers > 0 and posts_count > 0:
        er = round((likes / (followers * posts_count)) * 100, 4)
        
    conn = sqlite3.connect('newspaper_metrics.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO daily_stats (outlet_name, platform, record_date, followers, likes, posts_count, engagement_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (outlet, platform, today, followers, likes, posts_count, er))
    
    conn.commit()
    conn.close()

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
    print("Metrics logged.")
