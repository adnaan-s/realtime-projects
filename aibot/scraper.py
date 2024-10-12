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
    """Fetches the latest news using the Bing API for the given query."""
    headers = {'Ocp-Apim-Subscription-Key': API_KEY}
    params = {
        'q': f'{query} forex news',
        'count': 5,  # Fetch 5 news articles
        'mkt': 'en-US',
        'sortBy': 'Date'
    }

    try:
        response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        articles = response.json().get('value', [])

        # Debug output for the response structure
        print(f"Response for {query}: {response.json()}")  # Debug: Print the entire response

        if not articles:
            print(f"No news articles found for {query}.")
            return []

        return [article['name'] for article in articles]

    except requests.RequestException as e:
        print(f"Error fetching news for {query}: {e}")
        return []

def fetch_forex_news():
    """Fetches news for all defined forex pairs."""
    for pair in FOREX_PAIRS:
        print(f"Fetching news for {pair}...")  # Indicate which pair is being processed
        news = bing_search(pair)
        if news:
            news_cache[pair] = news
            print(f"News for {pair}:")
            for article in news:
                print(f"- {article}")  # Print each article
        else:
            print(f"No news found for {pair}.")

if __name__ == "__main__":
    # Initial fetch
    print("Starting initial news fetch...")  # Debug: Indicate the start of the fetch
    fetch_forex_news()

    # Schedule the scraping job to run every 5 minutes
    schedule.every(5).minutes.do(fetch_forex_news)

    print("News scraper started. Fetching news every 5 minutes.")  # Indicate that the scheduler is running

    # Run the scheduled scraping in the background
    while True:
        schedule.run_pending()
        time.sleep(60)
