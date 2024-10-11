def trading_decision(market_direction):
    if market_direction == 'bullish':
        return "Buy"
    elif market_direction == 'bearish':
        return "Sell"
    else:
        return "Hold"

if __name__ == "__main__":
    # Test the function
    test_directions = ['bullish', 'bearish', 'neutral']
    for direction in test_directions:
        decision = trading_decision(direction)
        print(f"Market direction: {direction}, Trading decision: {decision}")