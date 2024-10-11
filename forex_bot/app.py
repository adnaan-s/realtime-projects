from flask import Flask, jsonify
from scraper import bing_search  # Updated import for Bing search
from sentiment_model import analyze_sentiment
from predictor import trading_decision
from statistics import mean
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import datetime

app = Flask(__name__)
news_history_file = "news_history.json"  # File to store historical data

def calculate_overall_sentiment(sentiments):
    sentiment_scores = {'positive': 1, 'neutral': 0, 'negative': -1}
    scores = [sentiment_scores[s] for s in sentiments]
    return mean(scores) if scores else 0

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

    # Check if the historical data file exists before trying to open it
    if os.path.exists(news_history_file):
        with open(news_history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []

    # Add new data with timestamp
    history.append({
        'pair': pair,
        'timestamp': datetime.datetime.now().isoformat(),
        'news_analysis': news_analysis
    })

    # Write updated history back to file
    with open(news_history_file, 'w') as f:
        json.dump(history, f, indent=4)

def scrape_and_store_forex_news(pair):
    news = bing_search(f'{pair}')
    results = []
    sentiments = []

    for headline in news:
        sentiment = analyze_sentiment(headline)
        sentiments.append(sentiment)
        results.append({
            'headline': headline,
            'sentiment': sentiment
        })

    overall_sentiment = calculate_overall_sentiment(sentiments)
    market_direction = get_market_direction(overall_sentiment)
    prediction = trading_decision(market_direction.lower())

    # Store results in the historical file
    store_news_analysis(pair, {
        'overall_sentiment': overall_sentiment,
        'market_direction': market_direction,
        'prediction': prediction,
        'confidence': abs(overall_sentiment),
        'news_analysis': results
    })

@app.route('/forex_predict/<pair>')
def forex_predict(pair):
    # Read the most recent analysis from the historical data
    with open(news_history_file, 'r') as f:
        history = json.load(f)
    
    # Get the most recent analysis for the given pair
    recent_analysis = next((entry for entry in reversed(history) if entry['pair'] == pair), None)
    
    if recent_analysis:
        return jsonify(recent_analysis)
    else:
        return jsonify({"error": "No historical data found for this pair."}), 404

@app.route('/')
def home():
    return "Welcome to the Forex Prediction API. Use /forex_predict/<pair> to get the latest prediction."

# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=lambda: scrape_and_store_forex_news('EURUSD'), trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
