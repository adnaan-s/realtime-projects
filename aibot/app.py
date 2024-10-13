from flask import Flask, jsonify, request
from scraper import scrape_and_store_forex_news
import json
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import time
import asyncio
from metaapi_integration import execute_trade_for_signals
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
news_history_file = "news_history.json"
forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
bing_api_key = os.getenv('BING_API_KEY')

# Create a ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=1)

def get_real_time_price(pair):
    headers = {'Ocp-Apim-Subscription-Key': bing_api_key}
    params = {
        'q': f'{pair} forex real-time price',
        'count': 1,
        'mkt': 'en-US',
        'sortBy': 'Date'
    }

    try:
        time.sleep(2)
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
    with open(news_history_file, 'r') as f:
        history = json.load(f)

    recent_analysis = next((entry for entry in reversed(history) if entry['pair'] == pair), None)
    
    if recent_analysis:
        return jsonify(recent_analysis)
    else:
        return jsonify({"error": "No historical data found for this pair."}), 404

@app.route('/')
def home():
    if os.path.exists(news_history_file):
        with open(news_history_file, 'r') as f:
            history = json.load(f)

        if history:
            return jsonify(history), 200
    return jsonify({"error": "No news analysis available yet."}), 404

def run_async_trade(signals):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app.logger.info(f"Attempting to execute trades for signals: {signals}")
        result = loop.run_until_complete(execute_trade_for_signals(signals))
        app.logger.info(f"Trade execution result: {result}")
        return result
    except Exception as e:
        app.logger.error(f"Error executing trades: {e}")
        return {"error": str(e)}
    finally:
        loop.close()

@app.route('/trade-signals', methods=['POST'])
def trade_signals():
    signals = request.json
    
    app.logger.info(f"Received trade signals: {signals}")
    
    if not signals or not isinstance(signals, dict):
        app.logger.error("Invalid signals format received")
        return jsonify({"error": "Invalid signals format. Please provide a dictionary."}), 400

    try:
        # Run the async function in a separate thread
        future = executor.submit(run_async_trade, signals)
        result = future.result()
        
        app.logger.info(f"Trade execution completed. Result: {result}")
        
        if isinstance(result, dict) and "error" in result:
            app.logger.error(f"Error in trade execution: {result['error']}")
            return jsonify(result), 500
        return jsonify({"message": "Trades executed successfully", "details": result})
    except Exception as e:
        app.logger.error(f"Unexpected error in trade_signals route: {e}")
        return jsonify({"error": str(e)}), 500

scheduler = BackgroundScheduler()
scheduler.add_job(func=scrape_and_store_forex_news, trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    scrape_and_store_forex_news()
    app.run(debug=True)