import requests
import schedule
import time

# Store scraped news in a global dictionary
news_cache = {}

# Bing API credentials
API_KEY = '5fa27cea56a44bd4a4a3c7bd1f06ab49'
BING_SEARCH_URL = 'https://api.bing.microsoft.com/v7.0/news/search'

def bing_search(query):
    headers = {
        'Ocp-Apim-Subscription-Key': API_KEY
    }
    params = {
        'q': f'{query} forex news',
        'count': 5,  # Number of results to fetch
        'mkt': 'en-US',  # Language/market
        'sortBy': 'Date'  # Sort by date
    }

    try:
        response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching search results from Bing: {e}")
        return []

    search_results = response.json().get('value', [])
    
    if not search_results:
        print("Warning: No search results found.")
        return []

    # Extract text from the first 5 results
    return [result['name'] for result in search_results]

def continuous_scraping():
    forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY' 'XAUUSD']  # Add more pairs as needed
    for pair in forex_pairs:
        print(f"Fetching news for {pair}...")
        news = bing_search(pair)
        if news:
            news_cache[pair] = news
        else:
            print(f"No news found for {pair}.")

# Schedule the scraping job to run every 5 minutes
schedule.every(5).minutes.do(continuous_scraping)

if __name__ == "__main__":
    # Run the continuous scraper in the background
    continuous_scraping()  # Initial scrape
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute if a scheduled job needs to run
