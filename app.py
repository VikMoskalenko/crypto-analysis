from flask import Flask, render_template, request
import requests
import numpy as np

app = Flask(__name__)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
def get_top_cryptos():
    url = (f"{COINGECKO_API_URL}/coins/markets?vs_currency=usd&order=market_cap_desc"
           f"&per_page=10&page=1&sparkline=true&price_change_percentage=1h,24h,7d")
    response = requests.get(url).json()
    return response

def get_crypto_data(crypto_name):
    url = f"{COINGECKO_API_URL}/coins/{crypto_name.lower()}/market_chart?vs_currency=usd&days=30"
    response = requests.get(url).json()

    prices = [price[1] for price in response.get("prices", [])]
    return prices

def fibonacci_projection(prices):
    high = max(prices)
    low = min(prices)
    levels = [0.236, 0.382, 0.618]
    projections = {level: low + (high - low) * level for level in levels}
    return projections

def fibonacci_expected_changes(prices):
    projections = fibonacci_projection(prices)
    current_price = prices[-1]
    expected_changes = {}
    for level, proj in projections.items():
        percentage_change = ((proj - current_price) / current_price) * 100
        expected_changes[level] = percentage_change
    return expected_changes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/crypto', methods=['GET', 'POST'])
def crypto():
    top_cryptos = get_top_cryptos()
    analysis = None

    if request.method == 'POST':
        crypto_name = request.form.get('crypto_name')
        try:
            prices = get_crypto_data(crypto_name)
            expected_changes = fibonacci_expected_changes(prices)
            current_price = prices[-1]
            analysis_lines = [f"Current price of {crypto_name.title()}: ${current_price:.2f}"]
            for level, change in expected_changes.items():
                direction = "increase" if change > 0 else "decrease"
                analysis_lines.append(
                    f"At Fibonacci level {level:.3f}, expected {direction} of {abs(change):.2f}%."
                )
            analysis = " ".join(analysis_lines)
        except Exception as e:
            analysis = f"Error fetching data. Please check the cryptocurrency name. ({e})"

    return render_template('crypto.html', cryptos=top_cryptos, analysis=analysis)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

