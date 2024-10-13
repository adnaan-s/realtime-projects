from flask import Flask, jsonify
from scraper import scrape_and_store_forex_news  # Import the scraping function directly
import json
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import time  # Import time for managing request intervals

app = Flask(__name__)
news_history_file = "news_history.json"  # File to store historical data
forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']  # List of forex pairs to scrape
bing_api_key = '5fa27cea56a44bd4a4a3c7bd1f06ab49'  # Bing API key

def get_real_time_price(pair):
    """Fetch the real-time price for a given forex pair using Bing API."""
    headers = {'Ocp-Apim-Subscription-Key': bing_api_key}
    params = {
        'q': f'{pair} forex real-time price',
        'count': 1,
        'mkt': 'en-US',
        'sortBy': 'Date'
    }

    try:
        time.sleep(2)  # Introduce a delay to manage rate limits
        response = requests.get('https://api.bing.microsoft.com/v7.0/news/search', headers=headers, params=params)
        
        if response.status_code == 200:
            articles = response.json().get('value', [])
            if articles:
                return articles[0].get('name', 'No price data available')
            return 'No price data available'
        elif response.status_code == 429:
            print(f"Rate limit reached for {pair}.")
            return 'Rate limit reached'
        else:
            print(f"Error fetching price for {pair}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

@app.route('/forex_predict/<pair>')
def forex_predict(pair):
    """Fetch recent analysis for a given forex pair."""
    with open(news_history_file, 'r') as f:
        history = json.load(f)

    recent_analysis = next((entry for entry in reversed(history) if entry['pair'] == pair), None)
    
    if recent_analysis:
        return jsonify(recent_analysis)
    else:
        return jsonify({"error": "No historical data found for this pair."}), 404

@app.route('/')
def home():
    """Return the entire news analysis history."""
    if os.path.exists(news_history_file):
        with open(news_history_file, 'r') as f:
            history = json.load(f)

        if history:
            return jsonify(history), 200  # Return the entire history
    return jsonify({"error": "No news analysis available yet."}), 404

# Schedule scraping every 10 minutes for all pairs
scheduler = BackgroundScheduler()
scheduler.add_job(func=scrape_and_store_forex_news, trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    # Run initial scrape
    scrape_and_store_forex_news()
    app.run(debug=True)
