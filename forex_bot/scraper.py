import requests
from bs4 import BeautifulSoup
import urllib.parse
import schedule
import time

# Store scraped news in a global dictionary
news_cache = {}

def yahoo_search(query):
    encoded_query = urllib.parse.quote(f"{query} forex news")
    url = f"https://search.yahoo.com/search?p={encoded_query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Yahoo search results are typically in 'h3' tags with class 'title'
    search_results = soup.find_all('h3', class_='title')

    if not search_results:
        print("Warning: No search results found. The page structure might have changed.")
        return []

    # Extract text from the first 5 results
    return [result.get_text() for result in search_results[:5]]

def continuous_scraping():
    forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY']  # Add more pairs as needed
    for pair in forex_pairs:
        print(f"Scraping news for {pair}...")
        news = yahoo_search(pair)
        if news:
            news_cache[pair] = news
        else:
            print(f"No news found for {pair}.")

# Schedule the scraping job to run every hour
schedule.every(1).hour.do(continuous_scraping)

if __name__ == "__main__":
    # Run the continuous scraper in the background
    continuous_scraping()  # Initial scrape
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute if a scheduled job needs to run
