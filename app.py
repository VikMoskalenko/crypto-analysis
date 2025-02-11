from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import numpy as np
from datetime import datetime
from flask_login import login_user, logout_user, login_required
from forms import RegistrationForm, LoginForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
#from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2


app = Flask(__name__)


app.config["SECRET_KEY"] = "mysecretKey"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def get_db_connection():
    return psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1234", port=5432)


COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM customers WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return User(user[0], user[1], user[2])
    return None

def get_top_cryptos():
    url = (f"{COINGECKO_API_URL}/coins/markets?vs_currency=usd&order=market_cap_desc"
           f"&per_page=10&page=1&sparkline=true&price_change_percentage=1h,24h,7d")
    response = requests.get(url).json()
    for crypto in response:
        if 'last_updated' in crypto:
            dt = datetime.strptime(crypto['last_updated'], "%Y-%m-%dT%H:%M:%S.%fZ")
            crypto['last_updated'] = dt.strftime("%d/%m/%Y %H:%M")
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

def fibonacci_trade_signal(prices):
    projections = fibonacci_projection(prices)
    current_price = prices[-1]

    buy_signal = False
    sell_signal = False
    signal_reason = ""

    for level, proj in projections.items():
        change = ((proj - current_price) / current_price) * 100

        if -2 <= change <= 2:  # Close to a Fibonacci level
            if change < 0:  # Below Fibonacci level, potential buy
                buy_signal = True
                signal_reason = f"Consider buying. Price near support at level {level:.3f}."
            elif change > 0:  # Above Fibonacci level, potential sell
                sell_signal = True
                signal_reason = f"Consider selling. Price near resistance at level {level:.3f}."

    return buy_signal, sell_signal, signal_reason


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/crypto', methods=['GET', 'POST'])
def crypto():
    top_cryptos = get_top_cryptos()
    analysis = None
    recommendation = None

    if request.method == 'POST':
        crypto_name = request.form.get('crypto_name')
        try:
            prices = get_crypto_data(crypto_name)
            expected_changes = fibonacci_expected_changes(prices)
            current_price = prices[-1]
            analysis_lines = [f"Current price of {crypto_name.title()}: ${current_price:.2f}"]

            buy_signal = False
            sell_signal = False

            for level, change in expected_changes.items():
                direction = "increase" if change > 0 else "decrease"
                analysis_lines.append(
                    f"At Fibonacci level {level:.3f}, expected {direction} of {abs(change):.2f}%."
                )

                # Buy if price is predicted to drop significantly
                if direction == "decrease" and abs(change) >= 3:
                    buy_signal = True

                # Sell if price is predicted to rise significantly
                if direction == "increase" and change >= 3:
                    sell_signal = True

            if buy_signal:
                recommendation = "BUY"
            elif sell_signal:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"

            analysis = " ".join(analysis_lines)

        except Exception as e:
            analysis = f"Error fetching data. Please check the cryptocurrency name. ({e})"

    return render_template('crypto.html', cryptos=top_cryptos, analysis=analysis, recommendation=recommendation)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO customers (username, password) VALUES (%s, %s) RETURNING id", (username, hashed_password))
            conn.commit()
            user_id = cur.fetchone()[0]
            user = User(user_id, username, hashed_password)
            login_user(user)
            flash("Registration successful!", "success")
            return redirect(url_for('home'))
        except psycopg2.IntegrityError:
            conn.rollback()
            flash("Username already taken. Try another one.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM customers WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

