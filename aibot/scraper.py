import requests
import os
import json
from sentiment_model import analyze_sentiment_vader

bing_api_key = os.getenv('BING_API_KEY')
news_history_file = 'news_history.json'

def scrape_and_store_forex_news():
    forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    all_news = []

    headers = {'Ocp-Apim-Subscription-Key': bing_api_key}
    for pair in forex_pairs:
        params = {'q': f'{pair} forex news', 'count': 5, 'mkt': 'en-US', 'sortBy': 'Date'}
        response = requests.get('https://api.bing.microsoft.com/v7.0/news/search', headers=headers, params=params)
        
        if response.status_code == 200:
            news_data = response.json().get('value', [])
            for article in news_data:
                news = article.get('name', 'No title')
                timestamp = article.get('datePublished', 'No timestamp')

                # Analyze sentiment
                sentiment, confidence = analyze_sentiment_vader(news)

                # Store news with sentiment
                news_item = {
                    'pair': pair,
                    'news': news,
                    'timestamp': timestamp,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'price': 0  # Placeholder, to be updated with real-time price
                }
                all_news.append(news_item)
        else:
            print(f"Error fetching news for {pair}: {response.status_code}")

    # Save scraped news to a JSON file
    with open(news_history_file, 'w') as f:
        json.dump(all_news, f)

    print("Scraped and stored forex news.")
