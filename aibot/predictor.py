from sklearn.linear_model import LinearRegression
import numpy as np
import yfinance as yf
from sentiment_model import calculate_overall_sentiment

# Linear Regression Model for Price Prediction
def predict_price_movement(pair):
    """Predict future price movement based on historical data using linear regression."""
    data = yf.download(f'{pair}=X', period='1mo', interval='1d')  # Get one month of daily data
    data['returns'] = data['Close'].pct_change()  # Calculate daily returns
    data = data.dropna()  # Drop NaN values

    # Create features and labels
    X = np.array(range(len(data))).reshape(-1, 1)  # Day index
    y = data['Close'].values

    model = LinearRegression()
    model.fit(X, y)
    next_day_prediction = model.predict([[len(X)]])  # Predict next day's price

    return next_day_prediction[0]

# Advanced trading decision with price prediction factor
def trading_decision(market_direction, overall_sentiment, predicted_price):
    """
    Make trading decisions based on market direction, overall sentiment, and predicted price movement.
    """
    if market_direction == 'bullish':
        if overall_sentiment > 0.5 and predicted_price > 0:
            return "Buy - Strong Bullish Sentiment and Positive Price Prediction"
        elif 0 < overall_sentiment <= 0.5:
            return "Buy - Moderate Bullish Sentiment"
        else:
            return "Hold - Bullish but Uncertain Price Movement"

    elif market_direction == 'bearish':
        if overall_sentiment < -0.5 and predicted_price < 0:
            return "Sell - Strong Bearish Sentiment and Negative Price Prediction"
        elif -0.5 < overall_sentiment < 0:
            return "Sell - Moderate Bearish Sentiment"
        else:
            return "Hold - Bearish but Uncertain Price Movement"

    else:  # Neutral
        return "Hold - Market is Neutral"

if __name__ == "__main__":
    print("Testing trading decision with predictions...")
    test_sentiments = [0.6, -0.7, 0.1]
    test_predictions = [1.1, -0.5, 0.2]
    for sentiment, prediction in zip(test_sentiments, test_predictions):
        decision = trading_decision('bullish', sentiment, prediction)
        print(f"Overall sentiment: {sentiment}, Predicted price: {prediction}, Decision: {decision}")
