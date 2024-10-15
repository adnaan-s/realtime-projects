from flask import Flask, jsonify, request
from scraper import scrape_and_store_forex_news
import json
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from metaapi_integration import execute_trade_for_signals
from sentiment_model import train_model, predict_trade_action
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Load the trained model once and reuse it
model = train_model()

news_history_file = "news_history.json"
forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
bing_api_key = os.getenv('BING_API_KEY')

executor = ThreadPoolExecutor(max_workers=1)

# Fetch real-time price function using Bing API
def get_real_time_price(pair):
    headers = {'Ocp-Apim-Subscription-Key': bing_api_key}
    params = {
        'q': f'{pair} forex real-time price',
        'count': 1,
        'mkt': 'en-US',
        'sortBy': 'Date'
    }
    try:
        response = requests.get('https://api.bing.microsoft.com/v7.0/news/search', headers=headers, params=params)
        if response.status_code == 200:
            articles = response.json().get('value', [])
            if articles:
                return articles[0].get('name', 'No price data available')
            return 'No price data available'
        elif response.status_code == 429:
            app.logger.warning(f"Rate limit reached for {pair}.")
            return 'Rate limit reached'
        else:
            app.logger.error(f"Error fetching price for {pair}: {response.status_code}")
            return None
    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return None

@app.route('/forex_predict/<pair>')
def forex_predict(pair):
    # Load the historical news data and display latest relevant news
    with open(news_history_file, 'r') as f:
        history = json.load(f)

    recent_analysis = next((entry for entry in reversed(history) if entry['pair'] == pair), None)
    if recent_analysis:
        return jsonify(recent_analysis)
    else:
        return jsonify({"error": "No historical data found for this pair."}), 404

@app.route('/')
def home():
    # Display the most recent news and show predicted trade action
    if os.path.exists(news_history_file):
        with open(news_history_file, 'r') as f:
            history = json.load(f)

        if history:
            latest_news = history[0]

            # Predict trade action using ML model
            trade_action = predict_trade_action(
                model, 
                latest_news['sentiment'], 
                latest_news['confidence'], 
                latest_news['price']
            )

            return jsonify({
                "pair": latest_news['pair'],
                "news": latest_news['news'],
                "price": latest_news['price'],
                "sentiment": latest_news['sentiment'],
                "confidence": latest_news['confidence'],
                "timestamp": latest_news['timestamp'],
                "predicted_action": trade_action
            }), 200
    return jsonify({"error": "No news analysis available yet."}), 404

def run_async_trade(latest_news):
    # Predict the trade action using the trained model
    trade_action = predict_trade_action(
        model,
        latest_news['sentiment'],
        latest_news['confidence'],
        latest_news['price']
    )
    
    if trade_action == "buy":
        print("Executing buy order...")
    elif trade_action == "sell":
        print("Executing sell order...")
    else:
        print("Holding position...")

    return trade_action

@app.route('/trade-signals', methods=['POST'])
def trade_signals():
    signals = request.json
    if not signals or not isinstance(signals, dict):
        return jsonify({"error": "Invalid signals format. Please provide a dictionary."}), 400

    try:
        # Run the async function in a separate thread
        future = executor.submit(run_async_trade, signals)
        result = future.result()
        return jsonify({"message": "Trades executed successfully", "details": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

scheduler = BackgroundScheduler()
scheduler.add_job(func=scrape_and_store_forex_news, trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    scrape_and_store_forex_news()
    app.run(debug=True)
