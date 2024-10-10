from flask import Flask, jsonify
from scraper import yahoo_search
from sentiment_model import analyze_sentiment
from predictor import trading_decision
from statistics import mean

app = Flask(__name__)

def calculate_overall_sentiment(sentiments):
    sentiment_scores = {'positive': 1, 'neutral': 0, 'negative': -1}
    scores = [sentiment_scores[s] for s in sentiments]
    return mean(scores)

def get_market_direction(overall_sentiment):
    if overall_sentiment > 0.2:
        return "Bullish"
    elif overall_sentiment < -0.2:
        return "Bearish"
    else:
        return "Neutral"

@app.route('/forex_predict/<pair>')
def forex_predict(pair):
    news = yahoo_search(f'{pair}')
    
    results = []
    sentiments = []
    for headline in news:
        sentiment = analyze_sentiment(headline)
        sentiments.append(sentiment)
        results.append({
            'headline': headline,
            'sentiment': sentiment
        })

    overall_sentiment = calculate_overall_sentiment(sentiments)
    market_direction = get_market_direction(overall_sentiment)
    prediction = trading_decision(market_direction.lower())

    return jsonify({
        'forex_pair': pair,
        'overall_sentiment': overall_sentiment,
        'market_direction': market_direction,
        'prediction': prediction,
        'confidence': abs(overall_sentiment),  # Simple confidence measure
        'news_analysis': results
    })

@app.route('/')
def home():
    return "Welcome to the Forex Prediction API. Use /forex_predict/<pair> to get a prediction."

if __name__ == "__main__":
    app.run(debug=True)