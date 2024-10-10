import requests
from bs4 import BeautifulSoup
import re

def google_search(query):
    search_url = f"https://www.google.com/search?q={query}+forex+news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send request
    response = requests.get(search_url, headers=headers)
    
    # Check response status code
    if response.status_code != 200:
        print(f"Error: HTTP Status Code {response.status_code}")
        return []

    # Check for CAPTCHA
    if "Our systems have detected unusual traffic" in response.text:
        print("Error: Google CAPTCHA detected. Scraping is likely blocked.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for empty response
    if not soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd'):
        print("Error: No search results found. Possible blocking or empty response.")
        return []

    # Extract search results
    search_results = soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd')
    
    # Check for unexpected content
    if len(search_results) == 0:
        print("Error: Unexpected page content. Google may have changed their HTML structure.")
        return []

    return [result.get_text() for result in search_results[:5]]  # Return top 5 results

if __name__ == "__main__":
    news = google_search('EUR USD')
    print("Top 5 News Headlines for EUR/USD:")
    for headline in news:
        print(f"- {headline}")