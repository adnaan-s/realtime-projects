import requests
from bs4 import BeautifulSoup
import urllib.parse

def yahoo_search(query):
    encoded_query = urllib.parse.quote(f"{query} forex news")
    url = f"https://search.yahoo.com/search?p={encoded_query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: HTTP Status Code {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Yahoo search results are typically in 'h3' tags with class 'title'
    search_results = soup.find_all('h3', class_='title')
    
    if not search_results:
        print("Error: No search results found. The page structure might have changed.")
        return []

    # Extract text from the first 5 results
    return [result.get_text() for result in search_results[:5]]

if __name__ == "__main__":
    news = yahoo_search('EUR USD')
    print("Top 5 News Headlines for EUR/USD:")
    for headline in news:
        print(f"- {headline}")