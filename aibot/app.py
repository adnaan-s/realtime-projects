from flask import Flask, jsonify
from scraper import bing_search  # Import for Bing search
from sentiment_model import analyze_sentiment, calculate_overall_sentiment
from predictor import trading_decision
from statistics import mean
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import datetime
import requests

app = Flask(__name__)
news_history_file = "news_history.json"  # File to store historical data
forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']  # List of forex pairs to scrape
real_time_prices_api = "https://api.example.com/prices"  # Replace with actual real-time prices API

def get_real_time_price(pair):
    """Fetch the real-time price for a given forex pair."""
    try:
        response = requests.get(real_time_prices_api, params={'pair': pair})
        if response.status_code == 200:
            return response.json().get('price')
        else:
            print(f"Error fetching price for {pair}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def get_market_direction(overall_sentiment):
    if overall_sentiment > 0.2:
        return "Bullish"
    elif overall_sentiment < -0.2:
        return "Bearish"
    else:
        return "Neutral"

def store_news_analysis(pair, news_analysis):
    if not os.path.exists(news_history_file):
        with open(news_history_file, 'w') as f:
            json.dump([], f)

    with open(news_history_file, 'r') as f:
        history = json.load(f)

    history.append({
        'pair': pair,
        'timestamp': datetime.datetime.now().isoformat(),
        'news_analysis': news_analysis
    })

    with open(news_history_file, 'w') as f:
        json.dump(history, f, indent=4)

def scrape_and_store_forex_news():
    """Scrapes and stores news for all forex pairs."""
    for pair in forex_pairs:
        news = bing_search(f'{pair}')
        if not news:
            print(f"No news found for {pair}")
            continue

        results = []
        sentiments = []
        real_time_price = get_real_time_price(pair)

        for headline in news:
            sentiment = analyze_sentiment(headline)
            sentiments.append(sentiment)
            results.append({
                'headline': headline,
                'sentiment': sentiment
            })

        overall_sentiment = calculate_overall_sentiment(sentiments)
        market_direction = get_market_direction(overall_sentiment)
        prediction = trading_decision(market_direction.lower(), overall_sentiment)  # Pass overall sentiment

        # Store results
        store_news_analysis(pair, {
            'overall_sentiment': overall_sentiment,
            'market_direction': market_direction,
            'prediction': prediction,
            'confidence': abs(overall_sentiment),
            'real_time_price': real_time_price,  # Include real-time price
            'news_analysis': results
        })

@app.route('/forex_predict/<pair>')
def forex_predict(pair):
    with open(news_history_file, 'r') as f:
        history = json.load(f)

    recent_analysis = next((entry for entry in reversed(history) if entry['pair'] == pair), None)
    
    if recent_analysis:
        return jsonify(recent_analysis)
    else:
        return jsonify({"error": "No historical data found for this pair."}), 404

@app.route('/')
def home():
    # Read all news analysis from the historical data
    if os.path.exists(news_history_file):
        with open(news_history_file, 'r') as f:
            history = json.load(f)

        # Return all analyses
        if history:
            return jsonify(history), 200  # Return the entire history
    return "No news analysis available yet.", 404

# Schedule scraping every 10 minutes for all pairs
scheduler = BackgroundScheduler()
scheduler.add_job(func=scrape_and_store_forex_news, trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    # Run initial scrape
    scrape_and_store_forex_news()
    app.run(debug=True)