#conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="1234", port=5432)
# cur = conn.cursor()
# conn.commit()
# cur.execute("""CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY,
#         username VARCHAR(50) UNIQUE NOT NULL,
#         password VARCHAR(50) NOT NULL);""")
#
#
#
# cur.close()
# conn.close()
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/dbname'
# app.config["SECRET_KEY"] = "ffjdksleol,s78"

# def crypto():
#     top_cryptos = get_top_cryptos()
#     analysis = None
#
#     if request.method == 'POST':
#         crypto_name = request.form.get('crypto_name')
#         try:
#             prices = get_crypto_data(crypto_name)
#             expected_changes = fibonacci_expected_changes(prices)
#             current_price = prices[-1]
#             analysis_lines = [f"Current price of {crypto_name.title()}: ${current_price:.2f}"]
#             for level, change in expected_changes.items():
#                 direction = "increase" if change > 0 else "decrease"
#                 analysis_lines.append(
#                     f"At Fibonacci level {level:.3f}, expected {direction} of {abs(change):.2f}%."
#                 )
#             analysis = " ".join(analysis_lines)
#         except Exception as e:
#             analysis = f"Error fetching data. Please check the cryptocurrency name. ({e})"
#
#     return render_template('crypto.html', cryptos=top_cryptos, analysis=analysis)

# async def set_alert(update: Update, context: CallbackContext):
#     try:
#         args = context.args
#         if len(args) != 3:
#             await update.message.reply_text("Usage: /alert <crypto_name> <target_price> <buy/sell>")
#             return
#
#         crypto_name, target_price, action = args
#         target_price = float(target_price)
#
#         if action.lower() not in ["buy", "sell"]:
#             await update.message.reply_text("Action must be 'buy' or 'sell'.")
#             return
#
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute(
#             "INSERT INTO alerts (user_id, crypto_name, target_price, action) VALUES (%s, %s, %s, %s)",
#             (update.effective_user.id, crypto_name, target_price, action.lower()),
#         )
#         conn.commit()
#         cur.close()
#         conn.close()
#
#         await update.message.reply_text(f"✅ Alert set for {crypto_name} at ${target_price} ({action.upper()})")
#     except Exception as e:
#         await update.message.reply_text(f"Error: {e}")

# def check_alerts():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT user_id, crypto_name, target_price, action FROM alerts")
#     alerts = cur.fetchall()
#     cur.close()
#     conn.close()
#
#     messages = []
#     for user_id, crypto_name, target_price, action in alerts:
#         prices = requests.get(f"{COINGECKO_API_URL}/simple/price?ids={crypto_name}&vs_currencies=usd").json()
#         current_price = prices.get(crypto_name, {}).get("usd")
#
#         if not current_price:
#             continue
#
#         if (action == "buy" and current_price <= target_price) or (action == "sell" and current_price >= target_price):
#             messages.append((user_id,
#                              f"🔥 Alert: {crypto_name.title()} reached your {action.upper()} target! It's now ${current_price}."))
#
#     return messages
# async def show_favourites(update: Update, context: CallbackContext):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT crypto_name FROM favourites WHERE user_id = %s", (update.effective_user.id,))
#     favs = cur.fetchall()
#     cur.close()
#     conn.close()
#
#     if not favs:
#         await update.message.reply_text("You have no favourite cryptos yet! Use /crypto-alerts <crypto_name> to add one.")
#     else:
#         fav_list = "\n".join(f"- {fav[0].title()}" for fav in favs)
#         await update.message.reply_text(f"⭐ Your Favourite Cryptos:\n{fav_list}")

# async def show_cryptos(update: Update, context: CallbackContext):
#     cryptos = get_top_cryptos()
#     message = "📊 *Top 10 Cryptocurrencies:*\n\n"
#     for coin in cryptos:
#         message += f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}\n"
#
#     await update.message.reply_text(message)

# def get_top_cryptos():
#     url = f"{COINGECKO_API_URL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
#     return requests.get(url).json()
async def set_alert(update: Update, context: CallbackContext):
    """Set a buy/sell alert for a cryptocurrency."""
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Usage: /alerts_buy <crypto_name> <target_price> OR /alerts_sell <crypto_name> <target_price>")
            return

        crypto_name, target_price = args
        target_price = float(target_price)

        command = update.message.text.split()[0]
        action = "buy" if command == "/alerts_buy" else "sell"

        conn = get_db_connection()
        cur = conn.cursor()

        # Check for duplicate alerts
        cur.execute("SELECT 1 FROM alerts WHERE user_id = %s AND crypto_name = %s AND target_price = %s AND action = %s",
                    (update.effective_user.id, crypto_name.lower(), target_price, action))
        if cur.fetchone():
            await update.message.reply_text(f"⚠️ You already have an alert for {crypto_name} at ${target_price} ({action.upper()}).")
            cur.close()
            conn.close()
            return

        cur.execute(
            "INSERT INTO alerts (user_id, crypto_name, target_price, action) VALUES (%s, %s, %s, %s)",
            (update.effective_user.id, crypto_name.lower(), target_price, action),
        )
        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"✅ {action.upper()} alert set for {crypto_name} at ${target_price}!")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def set_alert(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Usage: /alerts_buy <crypto_name> <target_price> OR /alerts_sell <crypto_name> <target_price>")
            return

        crypto_name, target_price = args
        target_price = float(target_price)

        command = update.message.text.split()[0]
        action = "buy" if command == "/alerts_buy" else "sell"

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alerts (user_id, crypto_name, target_price, action) VALUES (%s, %s, %s, %s)",
            (update.effective_user.id, crypto_name.lower(), target_price, action),
        )
        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"✅ {action.upper()} alert set for {crypto_name} at ${target_price}!")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

        # def get_top_cryptos():
        #     url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        #     headers = {
        #         "Accepts": "application/json",
        #         "X-CMC_PRO_API_KEY": "4e16466f-343f-4464-9968-c6af96839fd1"
        #     }
        #
        #     response = requests.get(url, headers=headers).json()
        #
        #     # Extract data from CoinMarketCap response
        #     if response.get("status") and response["status"]["error_code"] == 0:
        #         cryptos = response.get("data", [])[:10]  # Get the top 10 cryptos
        #
        #         for crypto in cryptos:
        #             crypto["last_updated"] = datetime.strptime(
        #                 crypto["quote"]["USD"]["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ"
        #             ).strftime("%d/%m/%Y %H:%M")
        #
        #         return cryptos
        #     else:
        #         return []

        # @app.route('/crypto', methods=['GET', 'POST'])
        # def crypto():
        #     top_cryptos = get_top_cryptos()
        #     analysis = None
        #     recommendation = None
        #
        #     if request.method == 'POST':
        #         crypto_name = request.form.get('crypto_name')
        #         try:
        #             prices = get_crypto_data(crypto_name)
        #             expected_changes = fibonacci_expected_changes(prices)
        #             current_price = prices[-1]
        #             analysis_lines = [f"Current price of {crypto_name.title()}: ${current_price:.2f}"]
        #
        #             buy_signal = False
        #             sell_signal = False
        #
        #             for level, change in expected_changes.items():
        #                 direction = "increase" if change > 0 else "decrease"
        #                 analysis_lines.append(
        #                     f"At Fibonacci level {level:.3f}, expected {direction} of {abs(change):.2f}%."
        #                 )
        #
        #                 # Buy if price is predicted to drop significantly
        #                 if direction == "decrease" and abs(change) >= 3:
        #                     buy_signal = True
        #
        #                 # Sell if price is predicted to rise significantly
        #                 if direction == "increase" and change >= 3:
        #                     sell_signal = True
        #
        #             if buy_signal:
        #                 recommendation = "BUY"
        #             elif sell_signal:
        #                 recommendation = "SELL"
        #             else:
        #                 recommendation = "HOLD"
        #
        #             analysis = " ".join(analysis_lines)
        #
        #         except Exception as e:
        #             analysis = f"Error fetching data. Please check the cryptocurrency name. ({e})"
        #
        #     return render_template('crypto.html', cryptos=top_cryptos, analysis=analysis, recommendation=recommendation)
