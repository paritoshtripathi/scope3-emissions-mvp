
import requests

def generate_insights(raw_data):
    prompt = f"""
You are a sustainability intelligence agent. Given the following raw Scope 3 emissions data:

{raw_data}

1. What are the key KPIs that should be highlighted?
2. Which categories contribute the most to emissions?
3. Are there any anomalies or opportunities for reduction?
4. Format your response as a JSON array of tiles, cards, and charts for a dashboard. 
   Only use 'tile', 'chart', or 'card' as types. 
   Charts must specify 'chartType', 'labels', and 'values'.

Respond only in valid JSON.
"""

    response = requests.post(
        "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
        headers={"Authorization": "Bearer YOUR_HF_TOKEN"},
        json={"inputs": prompt}
    )

    try:
        output = response.json()
        return eval(output[0]["generated_text"])
    except Exception as e:
        return [{"type": "card", "message": f"Failed to generate insights: {str(e)}"}]
