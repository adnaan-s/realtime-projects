import json
import os
import requests
from sentiment_model import analyze_sentiment, calculate_overall_sentiment
from predictor import trading_decision
import time

news_history_file = "news_history.json"  # File to store historical data
bing_api_key = '5fa27cea56a44bd4a4a3c7bd1f06ab49'  # Bing API key

def scrape_and_store_forex_news():
    """Scrape forex news and store it in a JSON file."""
    forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']  # List of forex pairs to scrape
    news_data = []

    for pair in forex_pairs:
        news_articles = fetch_news(pair)
        if news_articles:
            news_data.extend(news_articles)

    if news_data:
        save_news_to_file(news_data)

def fetch_news(pair):
    """Fetch news articles for a given forex pair."""
    headers = {'Ocp-Apim-Subscription-Key': bing_api_key}
    params = {
        'q': f'{pair} forex news',
        'count': 10,  # Number of news articles to fetch
        'mkt': 'en-US'
    }

    try:
        response = requests.get('https://api.bing.microsoft.com/v7.0/news/search', headers=headers, params=params)
        if response.status_code == 200:
            articles = response.json().get('value', [])
            return process_news_articles(articles, pair)
        else:
            print(f"Error fetching news for {pair}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception occurred while fetching news for {pair}: {e}")
        return []

def process_news_articles(articles, pair):
    """Process and analyze news articles."""
    processed_articles = []
    sentiments = []

    for article in articles:
        headline = article.get('name', '')
        sentiment_score = analyze_sentiment(headline)
        sentiments.append(sentiment_score)

        processed_articles.append({
            'pair': pair,
            'headline': headline,
            'sentiment': sentiment_score,
            'url': article.get('url')
        })

    overall_sentiment = calculate_overall_sentiment(sentiments)
    signal = trading_decision('bullish' if overall_sentiment > 0 else 'bearish', overall_sentiment)

    # Add overall sentiment and signal to the news data
    if processed_articles:
        for article in processed_articles:
            article['overall_sentiment'] = overall_sentiment
            article['signal'] = signal

    return processed_articles

def save_news_to_file(news_data):
    """Save news data to a JSON file."""
    if os.path.exists(news_history_file):
        with open(news_history_file, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.extend(news_data)

    with open(news_history_file, 'w') as f:
        json.dump(existing_data, f, indent=4)

if __name__ == "__main__":
    scrape_and_store_forex_news()
