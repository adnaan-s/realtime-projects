# bing_search.py
import requests
import yfinance as yf

def bing_search(query):
    """Function to perform a Bing search for the given query."""
    headers = {'Ocp-Apim-Subscription-Key': '5fa27cea56a44bd4a4a3c7bd1f06ab49'}
    params = {
        'q': query,
        'count': 10,
        'mkt': 'en-US',
        'sortBy': 'Date'
    }
    
    try:
        response = requests.get('https://api.bing.microsoft.com/v7.0/news/search', headers=headers, params=params)
        if response.status_code == 200:
            articles = response.json().get('value', [])
            return [article.get('name') for article in articles]  # Extract headlines
        else:
            print(f"Error fetching news: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []

def get_real_time_price(pair):
    """Fetches the real-time price for the given forex pair using Yahoo Finance."""
    try:
        # Replace currency pair with the corresponding stock ticker if necessary
        ticker = f"{pair}=X"  # Assuming the format used in Yahoo Finance for forex pairs
        data = yf.Ticker(ticker)
        price = data.history(period='1m')['Close'].iloc[-1]  # Get the last closing price
        return price
    except Exception as e:
        print(f"Error fetching price for {pair}: {e}")
        return None
