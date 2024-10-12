import requests
import schedule
import time

# Bing API credentials
API_KEY = '5fa27cea56a44bd4a4a3c7bd1f06ab49'
BING_SEARCH_URL = 'https://api.bing.microsoft.com/v7.0/news/search'

# Store scraped news in a global dictionary
news_cache = {}

# List of forex pairs to track
FOREX_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']  # Added XAUUSD (Gold)

def bing_search(query):
    """Fetches the latest news using Bing API for the given query."""
    headers = {'Ocp-Apim-Subscription-Key': API_KEY}
    params = {
        'q': f'{query} forex news',
        'count': 5,  # Fetch 5 news articles
        'mkt': 'en-US',
        'sortBy': 'Date'
    }

    try:
        response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching search results from Bing for {query}: {e}")
        return []

    # Extract relevant news articles
    return [result['name'] for result in response.json().get('value', [])]

def fetch_forex_news():
    """Fetches news for all defined forex pairs."""
    for pair in FOREX_PAIRS:
        print(f"Fetching news for {pair}...")
        news = bing_search(pair)
        if news:
            news_cache[pair] = news
            print(f"News for {pair}: {news}")
        else:
            print(f"No news found for {pair}.")

# Schedule the scraping job to run every 5 minutes
schedule.every(5).minutes.do(fetch_forex_news)

if __name__ == "__main__":
    # Initial fetch
    fetch_forex_news()
    
    # Run the scheduled scraping in the background
    while True:
        schedule.run_pending()
        time.sleep(60)
