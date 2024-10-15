from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import os
import json

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Analyze sentiment using VADER
def analyze_sentiment_vader(news_text):
    """
    Analyzes the sentiment of the given text using VADER sentiment analysis.
    Returns a sentiment score and confidence value.
    """
    sentiment_scores = analyzer.polarity_scores(news_text)
    sentiment = sentiment_scores['compound']  # Compound score is a general sentiment score
    confidence = max(sentiment_scores['pos'], sentiment_scores['neg'], sentiment_scores['neu'])

    # Define sentiment labels based on compound score
    if sentiment >= 0.05:
        return 1, confidence  # Positive sentiment
    elif sentiment <= -0.05:
        return -1, confidence  # Negative sentiment
    else:
        return 0, confidence  # Neutral sentiment

# Load the training data from the news history JSON file
def load_training_data():
    """
    Loads the training data from the news history JSON file for model training.
    """
    if os.path.exists('news_history.json'):
        with open('news_history.json', 'r') as f:
            history = json.load(f)

        data = []
        for entry in history:
            data.append([
                entry['sentiment'], 
                entry['confidence'], 
                entry['price'],  
                entry.get('action', 0)  # Default action to 0 if not present
            ])
        return pd.DataFrame(data, columns=['sentiment', 'confidence', 'price', 'action'])
    return pd.DataFrame()

# Train the ML model (Random Forest)
def train_model():
    """
    Trains the RandomForestClassifier using the sentiment, confidence, and price data.
    """
    df = load_training_data()
    if df.empty:
        print("No training data found.")
        return None
    
    X = df[['sentiment', 'confidence', 'price']]
    y = df['action']

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate and print the model accuracy on test set
    accuracy = model.score(X_test, y_test)
    print("Model accuracy:", accuracy)
    
    return model

# Predict trade action (buy, sell, hold)
def predict_trade_action(model, sentiment, confidence, price):
    """
    Predicts the trade action (buy, sell, or hold) using the trained model.
    """
    X_new = np.array([[sentiment, confidence, price]])
    prediction = model.predict(X_new)
    
    if prediction == 1:
        return "buy"
    elif prediction == -1:
        return "sell"
    else:
        return "hold"

# Backtesting function
def backtest_model(model):
    """
    Backtest the trained model using historical news data.
    """
    df = load_training_data()
    if df.empty:
        print("No backtesting data available.")
        return

    X = df[['sentiment', 'confidence', 'price']]
    y = df['action']

    predictions = model.predict(X)
    accuracy = np.mean(predictions == y)
    print(f"Backtesting accuracy: {accuracy * 100:.2f}%")

    # Analyze trading results
    profit_loss = 0
    for i in range(len(predictions)):
        if predictions[i] == 1:  # Buy signal
            profit_loss += df.iloc[i]['price'] * 0.01  # Simulated profit on buy
        elif predictions[i] == -1:  # Sell signal
            profit_loss -= df.iloc[i]['price'] * 0.01  # Simulated loss on sell
    print(f"Total profit/loss from backtesting: {profit_loss:.2f}")
