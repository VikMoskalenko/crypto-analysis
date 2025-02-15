# import logging
# import requests
# import psycopg2
# import asyncio
# from telegram import Update, ReplyKeyboardMarkup
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
#
# COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
# TOKEN = "8130067595:AAHvxjw54rKEHQqLH32fzsz1fLjda9H9Tuo"
# DB_CONFIG = {
#     "host": "localhost",
#     "dbname": "postgres",
#     "user": "postgres",
#     "password": "1234",
#     "port": 5432
# }
#
# logging.basicConfig(level=logging.INFO)
# app = Application.builder().token(TOKEN).build()
#
#
# def get_db_connection():
#     return psycopg2.connect(**DB_CONFIG)
#
# def get_crypto_price(crypto_name):
#     """Fetch the current price of a cryptocurrency from CoinGecko."""
#     try:
#         url = f"{COINGECKO_API_URL}/simple/price?ids={crypto_name}&vs_currencies=usd"
#         response = requests.get(url).json()
#         return response.get(crypto_name, {}).get("usd")
#     except Exception as e:
#         logging.error(f"Error fetching price for {crypto_name}: {e}")
#         return None
#
# async def start(update: Update, context: CallbackContext):
#     await update.message.reply_text(
#         "Welcome to CryptoBot! 🚀\n"
#         "- View top 10 cryptocurrencies with /cryptos\n"
#         "- Set a buy/sell alert with /alerts_buy or /alerts_sell\n"
#         "- Manage favourites with /crypto_alerts\n"
#         "- View your favourites with /my_favourites"
#     )
#
# async def show_cryptos(update: Update, context: CallbackContext):
#     """Display top 10 cryptocurrencies with prices."""
#     try:
#         url = f"{COINGECKO_API_URL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
#         cryptos = requests.get(url).json()
#         message = "📊 *Top 10 Cryptocurrencies:*\n\n"
#         for coin in cryptos:
#             message += f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}\n"
#         await update.message.reply_text(message)
#     except Exception as e:
#         await update.message.reply_text(f"Error fetching crypto prices: {e}")
#
# async def set_alert(update: Update, context: CallbackContext):
#     """Set a buy/sell alert for a cryptocurrency."""
#     try:
#         args = context.args
#         if len(args) != 2:
#             await update.message.reply_text("Usage: /alerts_buy <crypto_name> <target_price> OR /alerts_sell <crypto_name> <target_price>")
#             return
#
#         crypto_name, target_price = args
#         target_price = float(target_price)
#
#         command = update.message.text.split()[0]
#         action = "buy" if command == "/alerts_buy" else "sell"
#
#         conn = get_db_connection()
#         cur = conn.cursor()
#
#         # Check for duplicate alerts
#         cur.execute(
#             "SELECT 1 FROM alerts WHERE user_id = %s AND crypto_name = %s AND target_price = %s AND action = %s",
#             (update.effective_user.id, crypto_name.lower(), target_price, action),
#         )
#         if cur.fetchone():
#             await update.message.reply_text(f"⚠️ You already have an alert for {crypto_name} at ${target_price} ({action.upper()}).")
#         else:
#             cur.execute(
#                 "INSERT INTO alerts (user_id, crypto_name, target_price, action) VALUES (%s, %s, %s, %s)",
#                 (update.effective_user.id, crypto_name.lower(), target_price, action),
#             )
#             conn.commit()
#             await update.message.reply_text(f"✅ {action.upper()} alert set for {crypto_name} at ${target_price}!")
#
#         cur.close()
#         conn.close()
#     except Exception as e:
#         await update.message.reply_text(f"Error: {e}")
# ##
#
# async def check_alerts():
#     """Check alerts and send notifications if targets are met."""
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT user_id, crypto_name, target_price, action FROM alerts")
#     alerts = cur.fetchall()
#     cur.close()
#     conn.close()
#
#     messages = []
#     for user_id, crypto_name, target_price, action in alerts:
#         current_price = get_crypto_price(crypto_name)
#
#         if current_price is None:
#             continue
#
#         if (action == "buy" and current_price <= target_price) or (action == "sell" and current_price >= target_price):
#             exchange_links = f"\n🔗 Buy/Sell on:\n- [Binance](https://www.binance.com)\n- [Coinbase](https://www.coinbase.com)\n- [Kraken](https://www.kraken.com)"
#             messages.append((user_id, f"🔥 Alert: {crypto_name.title()} reached your {action.upper()} target! It's now ${current_price}.{exchange_links}"))
#
#     return messages
#
#
#
# # async def send_notifications():
# #     messages = check_alerts()
# #     for user_id, message in messages:
# #         await app.bot.send_message(chat_id=user_id, text=message)
#
#
#
# async def check_alerts():
#     """Check alerts and send notifications if targets are met."""
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT id, user_id, crypto_name, target_price, action FROM alerts")
#     alerts = cur.fetchall()
#     cur.close()
#
#     messages = []
#     alert_ids_to_delete = []
#
#     for alert_id, user_id, crypto_name, target_price, action in alerts:
#         current_price = get_crypto_price(crypto_name)
#
#         if current_price is None:
#             continue
#
#         if (action == "buy" and current_price <= target_price) or (action == "sell" and current_price >= target_price):
#             messages.append((user_id, f"🔥 Alert: {crypto_name.title()} reached your {action.upper()} target! It's now ${current_price}.\n🔗 Buy/Sell on:\n- [Binance](https://www.binance.com)\n- [Coinbase](https://www.coinbase.com)\n- [Kraken](https://www.kraken.com)"))
#             alert_ids_to_delete.append(alert_id)
#
#     # Delete triggered alerts
#     if alert_ids_to_delete:
#         cur = conn.cursor()
#         cur.execute("DELETE FROM alerts WHERE id = ANY(%s)", (alert_ids_to_delete,))
#         conn.commit()
#         cur.close()
#
#     conn.close()
#     return messages
#
# async def send_notifications():
#     """Send alerts asynchronously to users."""
#     while True:
#         messages = await check_alerts()
#         for user_id, message in messages:
#             await app.bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
#         await asyncio.sleep(60)
#
# async def add_favourite(update: Update, context: CallbackContext):
#     """Add a cryptocurrency to the user's favourites."""
#     try:
#         args = context.args
#         if not args:
#             await update.message.reply_text("Usage: /crypto_alerts <crypto_name>")
#             return
#
#         crypto_name = args[0].lower()
#
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute(
#             "INSERT INTO favourites (user_id, crypto_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
#             (update.effective_user.id, crypto_name),
#         )
#         conn.commit()
#         cur.close()
#         conn.close()
#
#         await update.message.reply_text(f"⭐ {crypto_name.title()} added to your favourites!")
#     except Exception as e:
#         await update.message.reply_text(f"Error: {e}")
#
# async def show_favourites(update: Update, context: CallbackContext):
#     """Show the user's favourite cryptocurrencies."""
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT crypto_name FROM favourites WHERE user_id = %s", (update.effective_user.id,))
#     favs = cur.fetchall()
#     cur.close()
#     conn.close()
#
#     if not favs:
#         await update.message.reply_text("You have no favourite cryptos yet! Use /crypto_alerts <crypto_name> to add one.")
#     else:
#         fav_list = "\n".join(f"- {fav[0].title()}" for fav in favs)
#         await update.message.reply_text(f"⭐ Your Favourite Cryptos:\n{fav_list}")
#
#
#
# app.add_handler(CommandHandler("start", start))
# app.add_handler(CommandHandler("cryptos", show_cryptos))
# app.add_handler(CommandHandler("alerts_buy", set_alert))
# app.add_handler(CommandHandler("alerts_sell", set_alert))
# app.add_handler(CommandHandler("crypto_alerts", add_favourite))
# app.add_handler(CommandHandler("my_favourites", show_favourites))
#
#
#
# # Start bot polling
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.create_task(send_notifications())  # Start background task
#     app.run_polling()
