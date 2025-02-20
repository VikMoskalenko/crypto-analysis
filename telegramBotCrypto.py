import logging
import psycopg2
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import asyncio


#app = Flask(__name__)
COINMARKETCAP_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
HEADERS = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": "4e16466f-343f-4464-9968-c6af96839fd1"
}
TOKEN = "8130067595:AAHvxjw54rKEHQqLH32fzsz1fLjda9H9Tuo"
DB_CONFIG = {
    "host": "localhost",
    "dbname": "postgres",
    "user": "postgres",
    "password": "1234",
    "port": 5432
}

logging.basicConfig(level=logging.INFO)
app = Application.builder().token(TOKEN).build()

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_crypto_price(crypto_name):
    try:
        url = f"{COINMARKETCAP_API_URL}?symbol={crypto_name.upper()}&convert=USD"
        response = requests.get(url, headers=HEADERS).json()
        if 'data' in response and response['data']:
            return response['data'][0]['quote']['USD']['price']
        return None
    except Exception as e:
        logging.error(f"Error fetching price for {crypto_name}: {e}")
        return None

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to CryptoBot! 🚀\n"
        "- View top 10 cryptocurrencies with /cryptos\n"
        "- Set a buy/sell alert with /alerts_buy or /alerts_sell\n"
        "- Manage favourites with /crypto_alerts\n"
        "- View your favourites with /my_favourites\n"
        "- View your alerts with /my_alerts\n "
    )

async def show_cryptos(update: Update, context: CallbackContext):

    try:
        url = f"{COINMARKETCAP_API_URL}?limit=10&convert=USD"
        cryptos = requests.get(url, headers=HEADERS).json()
        message = "📊 *Top 10 Cryptocurrencies:*\n\n"
        for coin in cryptos['data']:
            message += f"{coin['name']} ({coin['symbol']}): ${coin['quote']['USD']['price']:.2f}\n"
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error fetching crypto prices: {e}")

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
            "SELECT 1 FROM alerts WHERE user_id = %s AND crypto_name = %s AND target_price = %s AND action = %s",
            (update.effective_user.id, crypto_name.lower(), target_price, action),
        )
        if cur.fetchone():
            await update.message.reply_text(f"⚠️ You already have an alert for {crypto_name} at ${target_price} ({action.upper()}).")
        else:
            cur.execute(
                "INSERT INTO alerts (user_id, crypto_name, target_price, action) VALUES (%s, %s, %s, %s)",
                (update.effective_user.id, crypto_name.lower(), target_price, action),
            )
            conn.commit()
            await update.message.reply_text(f"✅ {action.upper()} alert set for {crypto_name} at ${target_price}!")

        cur.close()
        conn.close()
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def check_alerts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, crypto_name, target_price, action FROM alerts")
    alerts = cur.fetchall()
    cur.close()

    messages = []
    alert_ids_to_delete = []

    for alert_id, user_id, crypto_name, target_price, action in alerts:
        current_price = get_crypto_price(crypto_name)

        if current_price is None:
            continue

        if (action == "buy" and current_price <= target_price) or (action == "sell" and current_price >= target_price):
            messages.append((user_id, f"🔥 Alert: {crypto_name.title()} reached your {action.upper()} target! It's now ${current_price}.\n🔗 Buy/Sell on:\n- [Binance](https://www.binance.com)\n- [Coinbase](https://www.coinbase.com)\n- [Kraken](https://www.kraken.com)"))
            alert_ids_to_delete.append(alert_id)

    if alert_ids_to_delete:
        cur = conn.cursor()
        cur.execute("DELETE FROM alerts WHERE id = ANY(%s)", (alert_ids_to_delete,))
        conn.commit()
        cur.close()

    conn.close()
    return messages

async def send_notifications():
    while True:
        messages = await check_alerts()
        for user_id, message in messages:
            await app.bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
        await asyncio.sleep(60)

async def add_favourite(update: Update, context: CallbackContext):
    try:
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /crypto_alerts <crypto_name>")
            return

        crypto_name = args[0].lower()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO favourites (user_id, crypto_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (update.effective_user.id, crypto_name),
        )
        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"⭐ {crypto_name.title()} added to your favourites!")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def show_favourites(update: Update, context: CallbackContext):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT crypto_name FROM favourites WHERE user_id = %s", (update.effective_user.id,))
    favs = cur.fetchall()
    cur.close()
    conn.close()

    if not favs:
        await update.message.reply_text("You have no favourite cryptos yet! Use /crypto_alerts <crypto_name> to add one.")
    else:
        fav_list = "\n".join(f"- {fav[0].title()}" for fav in favs)
        await update.message.reply_text(f"⭐ Your Favourite Cryptos:\n{fav_list}")

async def show_active_alerts(update: Update, context: CallbackContext):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT crypto_name, target_price, action FROM alerts WHERE user_id = %s", (update.effective_user.id,))
    alerts = cur.fetchall()
    cur.close()
    conn.close()

    if not alerts:
        await update.message.reply_text("You have no active alerts. Set one using /alerts_buy or /alerts_sell.")
    else:
        alert_list = "\n".join(f"{action.upper()} alert for {crypto_name.title()} at ${target_price}" for crypto_name, target_price, action in alerts)
        await update.message.reply_text(f"🔔 Your Active Alerts:\n{alert_list}")


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cryptos", show_cryptos))
app.add_handler(CommandHandler("alerts_buy", set_alert))
app.add_handler(CommandHandler("alerts_sell", set_alert))
app.add_handler(CommandHandler("crypto_alerts", add_favourite))
app.add_handler(CommandHandler("my_favourites", show_favourites))
app.add_handler(CommandHandler("my_alerts", show_active_alerts))


# Start bot polling
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(send_notifications())  # Start background task
    app.run_polling()
