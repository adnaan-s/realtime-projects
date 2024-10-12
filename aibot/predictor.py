# predictor.py

from os import name


def trading_decision(market_direction, overall_sentiment):
    """
    Make trading decisions based on market direction and overall sentiment.
    """
    # Implement multiple strategies
    if market_direction == 'bullish':
        # Momentum Strategy: Buy if sentiment is strong
        if overall_sentiment > 0.5:
            return "Buy - Strong Bullish Sentiment"
        elif 0 < overall_sentiment <= 0.5:
            return "Buy - Moderate Bullish Sentiment"
        else:
            return "Hold - Bullish but Low Sentiment"

    elif market_direction == 'bearish':
        # Momentum Strategy: Sell if sentiment is strong
        if overall_sentiment < -0.5:
            return "Sell - Strong Bearish Sentiment"
        elif -0.5 < overall_sentiment < 0:
            return "Sell - Moderate Bearish Sentiment"
        else:
            return "Hold - Bearish but Low Sentiment"

    else:  # Neutral
        return "Hold - Market is Neutral"

if name == "main":
    # Test the function
    test_directions = ['bullish', 'bearish', 'neutral']
    test_sentiments = [0.6, -0.7, 0]  # Example sentiment values
    for direction, sentiment in zip(test_directions, test_sentiments):
        decision = trading_decision(direction, sentiment)
        print(f"Market direction: {direction}, Overall sentiment: {sentiment}, Trading decision: {decision}")