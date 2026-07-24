import json
import openai
from supabase import create_client

def get_latest_data(supabase_url, supabase_key):
    supabase = create_client(supabase_url, supabase_key)
    response = supabase.table('daily_stats').select('*').order('record_date', desc=True).limit(18).execute()
    return response.data

def generate_ai_insights(openai_key, supabase_url, supabase_key):
    data = get_latest_data(supabase_url, supabase_key)
    if not data:
        return "No data available in the cloud database yet."

    client = openai.OpenAI(api_key=openai_key)
    
    prompt = f"""
    You are an expert social media analyst for news publications.
    Analyze the following recent dataset across three newspapers: Deadline, The Edinburgh Reporter, and The Glasgow Reporter.

    Dataset:
    {json.dumps(data, indent=2)}

    Please generate a concise executive summary covering:
    1. Top Performing Channel: Which outlet/platform combination has the healthiest engagement rate?
    2. Growth vs Engagement: Are larger publications suffering from lower proportional engagement?
    3. Key Recommendation: One actionable recommendation for regional outlets to boost reach.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content
