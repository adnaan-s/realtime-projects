from textblob import TextBlob

def analyze_sentiment(headline):
    try:
        analysis = TextBlob(headline)
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity < 0:
            return 'negative'
        else:
            return 'neutral'
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return 'neutral'  # Default to neutral if there's an error

if __name__ == "__main__":
    # Test the function
    test_headlines = [
        "The dollar is strengthening against the euro.",
        "Forex market faces uncertainty amid global tensions.",
        "New economic policy expected to boost currency values."
    ]
    for headline in test_headlines:
        sentiment = analyze_sentiment(headline)
        print(f"Headline: '{headline}'\nSentiment: {sentiment}\n")
