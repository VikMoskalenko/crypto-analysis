# import requests
# from flask import Flask, render_template, request
# from flask_login import UserMixin, LoginManager
# from datetime import datetime
# import psycopg2
#
# app = Flask(__name__)
#
#
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"
#
#
# COINMARKETCAP_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
# HEADERS = {
#     "Accepts": "application/json",
#     "X-CMC_PRO_API_KEY": "4e16466f-343f-4464-9968-c6af96839fd1"
# }
# def get_db_connection():
#     return psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1234", port=5432)
# class User(UserMixin):
#     def __init__(self, id, username, password):
#         self.id = id
#         self.username = username
#         self.password = password
#
# @login_manager.user_loader
# def load_user(user_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id, username, password FROM customers WHERE id = %s", (user_id,))
#     user = cur.fetchone()
#     cur.close()
#     conn.close()
#
#     if user:
#         return User(user[0], user[1], user[2])
#     return None
#
#
# def get_top_cryptos():
#     url = f"{COINMARKETCAP_API_URL}?limit=10&convert=USD"
#     response = requests.get(url, headers=HEADERS).json()
#
#     if "data" not in response:
#         return []
#
#     cryptos = []
#     for crypto in response["data"]:
#         cryptos.append({
#             "name": crypto["name"],
#             "symbol": crypto["symbol"],
#             # "current_price": crypto["quote"]["USD"]["price"],
#             # "price_change_percentage_1h_in_currency": crypto["quote"]["USD"]["percent_change_1h"],
#             # "price_change_percentage_24h_in_currency": crypto["quote"]["USD"]["percent_change_24h"],
#             # "price_change_percentage_7d_in_currency": crypto["quote"]["USD"]["percent_change_7d"],
#             "current_price": crypto["quote"]["USD"]["price"],
#             "change_24h": crypto["quote"]["USD"]["percent_change_24h"],
#             "total_volume": crypto["quote"]["USD"]["volume_24h"],
#             "market_cap": crypto["quote"]["USD"]["market_cap"],
#             "last_updated": datetime.strptime(crypto["quote"]["USD"]["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y %H:%M")
#         })
#     return cryptos
#
#
# def get_crypto_data(crypto_name):
#     url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical"
#     headers = {
#         "Accepts": "application/json",
#         "X-CMC_PRO_API_KEY": "4e16466f-343f-4464-9968-c6af96839fd1"
#     }
#
#     # Fetch the last 30 days' data for the cryptocurrency
#     params = {
#         "symbol": crypto_name.upper(),
#         "convert": "USD",
#         "time_end": "today",  # End of the period
#         "time_start": "30d",  # Last 30 days
#     }
#
#     response = requests.get(url, headers=headers, params=params).json()
#
#     if "data" not in response or response["status"]["error_code"] != 0:
#         print(f"API error for {crypto_name}: {response}")
#         return []
#
#     try:
#         crypto_data = response["data"].get(crypto_name.upper(), {}).get("quotes", [])
#         if not crypto_data:
#             print(f"No historical data found for {crypto_name}")
#             return []
#
#         # Extract the closing prices for the last 30 days
#         prices = [quote["close"] for quote in crypto_data]
#         return prices
#     except KeyError as e:
#         print(f"KeyError: {e} - Response: {response}")
#         return []
#
#
# def fibonacci_projection(prices):
#     high = max(prices)
#     low = min(prices)
#     levels = [0.236, 0.382, 0.618]
#     projections = {level: low + (high - low) * level for level in levels}
#     return projections
#
# def fibonacci_expected_changes(prices):
#     projections = fibonacci_projection(prices)
#     current_price = prices[-1]
#     expected_changes = {}
#     for level, proj in projections.items():
#         percentage_change = ((proj - current_price) / current_price) * 100
#         expected_changes[level] = percentage_change
#     return expected_changes
#
# def fibonacci_trade_signal(prices):
#     projections = fibonacci_projection(prices)
#     current_price = prices[-1]
#
#     buy_signal = False
#     sell_signal = False
#     signal_reason = ""
#
#     for level, proj in projections.items():
#         change = ((proj - current_price) / current_price) * 100
#
#         if -2 <= change <= 2:  # Close to a Fibonacci level
#             if change < 0:  # Below Fibonacci level, potential buy
#                 buy_signal = True
#                 signal_reason = f"Consider buying. Price near support at level {level:.3f}."
#             elif change > 0:  # Above Fibonacci level, potential sell
#                 sell_signal = True
#                 signal_reason = f"Consider selling. Price near resistance at level {level:.3f}."
#
#     return buy_signal, sell_signal, signal_reason
#
#
# @app.route('/')
# def home():
#     return render_template('index.html')
#
# @app.route('/crypto', methods=['GET', 'POST'])
# def crypto():
#     top_cryptos = get_top_cryptos()  # List of top cryptocurrencies
#     analysis = None
#     recommendation = None
#
#     if request.method == 'POST':
#         crypto_name = request.form.get('crypto_name').upper()  # Get user input for crypto name
#         try:
#             # Get the last 30 days' closing prices for Fibonacci analysis
#             prices = get_crypto_data(crypto_name)
#
#             # Ensure we have enough data for analysis
#             if len(prices) < 2:
#                 analysis = "Not enough data to perform analysis. Try again later."
#             else:
#                 # Perform Fibonacci analysis
#                 expected_changes = fibonacci_expected_changes(prices)
#                 current_price = prices[-1]  # Last value is the current price
#                 analysis_lines = [f"Current price of {crypto_name.title()}: ${current_price:.2f}"]
#
#                 buy_signal = False
#                 sell_signal = False
#
#                 # Analyze Fibonacci levels for price changes
#                 for level, change in expected_changes.items():
#                     direction = "increase" if change > 0 else "decrease"
#                     analysis_lines.append(
#                         f"At Fibonacci level {level:.3f}, expected {direction} of {abs(change):.2f}%."
#                     )
#
#                     # Buy if price is predicted to drop significantly
#                     if direction == "decrease" and abs(change) >= 3:
#                         buy_signal = True
#
#                     # Sell if price is predicted to rise significantly
#                     if direction == "increase" and change >= 3:
#                         sell_signal = True
#
#                 if buy_signal:
#                     recommendation = "BUY"
#                 elif sell_signal:
#                     recommendation = "SELL"
#                 else:
#                     recommendation = "HOLD"
#
#                 analysis = " ".join(analysis_lines)
#
#         except Exception as e:
#             analysis = f"Error fetching data. Please check the cryptocurrency name. ({e})"
#
#     return render_template('crypto.html', cryptos=top_cryptos, analysis=analysis, recommendation=recommendation)