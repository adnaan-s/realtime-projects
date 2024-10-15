import os
import requests
import json
import time
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Cache directory and expiration time (1 day)
CACHE_DIR = "cache"
CACHE_EXPIRY_HOURS = 24

# Ensure cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def bing_search(query):
    """Function to perform a Bing search for the given query, with caching and rate limit handling."""
    bing_api_key = os.getenv('BING_API_KEY')
    if not bing_api_key:
        raise ValueError("BING_API_KEY not found in environment variables")
    
    cache_file = os.path.join(CACHE_DIR, f"{query.replace(' ', '_')}_news.json")
    
    # Check if cached data is available and not expired
    if os.path.exists(cache_file):
        last_modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - last_modified_time < timedelta(hours=CACHE_EXPIRY_HOURS):
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            print("Returning cached news data")
            return cached_data
    
    headers = {'Ocp-Apim-Subscription-Key': bing_api_key}
    params = {
        'q': query,
        'count': 10,
        'mkt': 'en-US',
        'sortBy': 'Date'
    }
    
    try:
        response = requests.get('https://api.bing.microsoft.com/v7.0/news/search', headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        articles = response.json().get('value', [])
        
        # Cache the news data
        with open(cache_file, 'w') as f:
            json.dump(articles, f, indent=4)
        print("Fetched and cached new data from Bing")
        
        return [article.get('name') for article in articles]  # Extract headlines
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return []

def get_real_time_price(pair):
    """Fetches the real-time price for the given forex pair using Yahoo Finance."""
    try:
        ticker = f"{pair}=X"  # Format used in Yahoo Finance for forex pairs
        data = yf.Ticker(ticker)
        price = data.history(period='1m')['Close'].iloc[-1]  # Get the last closing price
        return price
    except Exception as e:
        print(f"Error fetching price for {pair}: {e}")
        return None

if __name__ == "__main__":
    # Test the functions
    print("Testing Bing Search:")
    results = bing_search("EURUSD forex news")
    for i, headline in enumerate(results, 1):
        print(f"{i}. {headline}")

    print("\nTesting Real-time Price:")
    price = get_real_time_price("EURUSD")
    if price:
        print(f"EURUSD current price: {price}")
    else:
        print("Failed to fetch EURUSD price")
