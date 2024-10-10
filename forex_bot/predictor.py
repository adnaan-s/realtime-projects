def trading_decision(sentiment):
    if sentiment == 'positive':
        return "Buy"
    elif sentiment == 'negative':
        return "Sell"
    else:
        return "Hold"

if __name__ == "__main__":
    # Simulate trading decision based on sentiment
    sentiment = 'positive'
    decision = trading_decision(sentiment)
    print(f"Trading decision: {decision}")
