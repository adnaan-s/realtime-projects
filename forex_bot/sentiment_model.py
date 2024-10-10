from textblob import TextBlob

def analyze_sentiment(headline):
    analysis = TextBlob(headline)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

if __name__ == "__main__":
    sample_headline = "The dollar is strengthening against the euro."
    sentiment = analyze_sentiment(sample_headline)
    print(f"The sentiment of the headline is {sentiment}.")
