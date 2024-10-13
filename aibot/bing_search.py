import os
import requests
import yfinance as yf
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def bing_search(query):
    """Function to perform a Bing search for the given query."""
    bing_api_key = os.getenv('BING_API_KEY')
    if not bing_api_key:
        raise ValueError("BING_API_KEY not found in environment variables")

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