import os
from flask import Flask, render_template, request
import requests
#from flask_login import UserMixin, LoginManager
from datetime import datetime
import psycopg2
app = Flask(__name__)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

BINANCE_API_URL = "https://api.binance.com"
def get_db_connection():
    return psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1234", port=5432)

# class User(UserMixin):
#     def __init__(self, id, username, password):
#         self.id = id
#         self.username = username
#         self.password = password

# @login_manager.user_loader
# def load_user(user_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id, username, password FROM customers WHERE id = %s", (user_id,))
#     user = cur.fetchone()
#     cur.close()
#     conn.close()
#     return User(user[0], user[1], user[2]) if user else None


def get_top_cryptos():
    url = f"{BINANCE_API_URL}/api/v3/ticker/24hr"
    response = requests.get(url).json()

    if not isinstance(response, list):
        return []

    top_cryptos = []
    for crypto in response[:10]:
        try:
            top_cryptos.append({
                "name": crypto.get("symbol", "Unknown"),
                "symbol": crypto.get("symbol", "Unknown"),
                "current_price": "{:.8f}".format(float(crypto["lastPrice"])) if "lastPrice" in crypto else "0.00000000",
                "change_24h": float(crypto["priceChangePercent"]) if "priceChangePercent" in crypto else 0.0,
                "total_volume": float(crypto["volume"]) if "volume" in crypto else 0.0,
                "market_cap": None,
                "last_updated": datetime.utcnow().strftime("%d/%m/%Y %H:%M")
            })
        except (KeyError, ValueError, TypeError) as e:
            print(f"Skipping invalid crypto entry due to error: {e}")

    return top_cryptos
# def get_top_cryptos():
#     url = "https://api.coingecko.com/api/v3/coins/markets"
#     params = {
#         "vs_currency": "usd",
#         "order": "market_cap_desc",  # Sort by market cap (largest first)
#         "per_page": 10,  # Get top 10
#         "page": 1,
#         "sparkline": False
#     }
#
#     response = requests.get(url, params=params)
#
#     if response.status_code != 200:
#         print("Error fetching data:", response.text)
#         return []
#
#     data = response.json()
#     top_cryptos = []
#
#     for crypto in data:
#         top_cryptos.append({
#             "name": crypto.get("name", "Unknown"),
#             "symbol": crypto.get("symbol", "Unknown").upper(),
#             "current_price": crypto.get("current_price", 0),
#             "change_24h": crypto.get("price_change_percentage_24h", 0),
#             "total_volume": crypto.get("total_volume", 0),
#             "market_cap": crypto.get("market_cap", 0),
#             "last_updated": datetime.utcnow().strftime("%d/%m/%Y %H:%M")
#         })
#
#     return top_cryptos

def get_30d_trading_volume(symbol):
    url = f"{BINANCE_API_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 30
    }
    response = requests.get(url, params=params).json()

    if not response or "code" in response:
        return None

    return sum(float(data[5]) for data in response)


def get_crypto_data(crypto_name):
    url = f"{BINANCE_API_URL}/api/v3/klines?symbol={crypto_name}USDT&interval=1d&limit=10"
    response = requests.get(url).json()

    if not isinstance(response, list) or len(response) == 0:
        print(f"API Error: No data returned for {crypto_name}")
        return []

    return [float(data[4]) for data in response]

def fibonacci_projection(prices):
    high = max(prices)
    low = min(prices)
    levels = [0.236, 0.382, 0.618]
    return {level: low + (high - low) * level for level in levels}


def fibonacci_expected_changes(prices):
    projections = fibonacci_projection(prices)
    current_price = prices[-1]
    return {level: ((proj - current_price) / current_price) * 100 for level, proj in projections.items()}
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/crypto', methods=['GET', 'POST'])
def crypto():
    top_cryptos = get_top_cryptos()
    print(top_cryptos)
    analysis = None
    recommendation = None

    if request.method == 'POST':
        crypto_name = request.form.get('crypto_name').upper()

        crypto_symbols = {
            "BITCOIN": "BTC",
            "ETHEREUM": "ETH",
            "SOLANA": "SOL",
        }
        crypto_symbol = crypto_symbols.get(crypto_name, crypto_name)

        prices = get_crypto_data(crypto_symbol)

        if len(prices) < 2:
            analysis = "Not enough data to perform analysis."
        else:
            expected_changes = fibonacci_expected_changes(prices)
            current_price = prices[-1]
            analysis_lines = [f"Current price of {crypto_symbol}: ${current_price:.2f}"]

            buy_signal, sell_signal = False, False
            for level, change in expected_changes.items():
                direction = "increase" if change > 0 else "decrease"
                analysis_lines.append(
                    f"At Fibonacci level {level:.3f}, expected {direction} of {abs(change):.2f}%."
                )

                if direction == "decrease" and abs(change) >= 3:
                    buy_signal = True
                if direction == "increase" and change >= 3:
                    sell_signal = True

            recommendation = "BUY" if buy_signal else "SELL" if sell_signal else "HOLD"
            analysis = " ".join(analysis_lines)

    return render_template('crypto.html', cryptos=top_cryptos, analysis=analysis, recommendation=recommendation)

@app.route('/test', methods=['GET', 'POST'])
def test():
    return "Test route is working!"

if __name__ == '__main__':
    app.run(debug=True)
