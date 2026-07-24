import sqlite3

def init_db():
    conn = sqlite3.connect('newspaper_metrics.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            outlet_name TEXT NOT NULL,
            platform TEXT NOT NULL,
            record_date DATE NOT NULL,
            followers INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            posts_count INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
