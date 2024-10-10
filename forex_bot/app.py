from flask import Flask, jsonify
from scraper import google_search
from sentiment_model import analyze_sentiment
from predictor import trading_decision

app = Flask(__name__)

@app.route('/forex_search/<pair>')
def forex_search(pair):
    news = google_search(f'{pair}')
    sentiment_results = [analyze_sentiment(headline) for headline in news]
    decisions = [trading_decision(sentiment) for sentiment in sentiment_results]

    return jsonify({
        'forex_news': news,
        'sentiments': sentiment_results,
        'trading_decisions': decisions
    })

if __name__ == "__main__":
    app.run(debug=True)
