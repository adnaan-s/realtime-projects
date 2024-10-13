from textblob import TextBlob

def analyze_sentiment(headline):
    """
    Analyze sentiment of the given headline.
    """
    try:
        analysis = TextBlob(headline)
        if analysis.sentiment.polarity > 0.5:
            return 1  # Strongly positive
        elif 0 < analysis.sentiment.polarity <= 0.5:
            return 0.5  # Positive
        elif analysis.sentiment.polarity < -0.5:
            return -1  # Strongly negative
        elif -0.5 < analysis.sentiment.polarity < 0:
            return -0.5  # Negative
        else:
            return 0  # Neutral
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return 0  # Default to neutral if there's an error

def calculate_overall_sentiment(sentiment_list):
    """
    Calculate the overall sentiment score based on individual sentiment scores.
    """
    if not sentiment_list:
        return 0
    return sum(sentiment_list) / len(sentiment_list)

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
