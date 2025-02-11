import logging
import requests
import psycopg2
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
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

def get_top_cryptos():
    url = f"{COINGECKO_API_URL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    return requests.get(url).json()

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to CryptoBot! 🚀\nYou can:\n"
        "- View top 10 cryptocurrencies\n"
        "- Set a buy/sell alert\n"
        "Use /alerts-buy or /alerts-sell to set alert\n"
        "Use /crypto-fav to choose favourites"
        "Use /cryptos to see the top 10 coins."
    )

async def show_cryptos(update: Update, context: CallbackContext):
    cryptos = get_top_cryptos()
    message = "📊 *Top 10 Cryptocurrencies:*\n\n"
    for coin in cryptos:
        message += f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}\n"

    await update.message.reply_text(message)

async def set_alert(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Usage: /alert <crypto_name> <target_price> <buy/sell>")
            return

        crypto_name, target_price, action = args
        target_price = float(target_price)

        if action.lower() not in ["buy", "sell"]:
            await update.message.reply_text("Action must be 'buy' or 'sell'.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alerts (user_id, crypto_name, target_price, action) VALUES (%s, %s, %s, %s)",
            (update.effective_user.id, crypto_name, target_price, action.lower()),
        )
        conn.commit()
        cur.close()
        conn.close()

        await update.message.reply_text(f"✅ Alert set for {crypto_name} at ${target_price} ({action.upper()})")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def check_alerts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, crypto_name, target_price, action FROM alerts")
    alerts = cur.fetchall()
    cur.close()
    conn.close()

    messages = []
    for user_id, crypto_name, target_price, action in alerts:
        prices = requests.get(f"{COINGECKO_API_URL}/simple/price?ids={crypto_name}&vs_currencies=usd").json()
        current_price = prices.get(crypto_name, {}).get("usd")

        if not current_price:
            continue

        if (action == "buy" and current_price <= target_price) or (action == "sell" and current_price >= target_price):
            messages.append((user_id,
                             f"🔥 Alert: {crypto_name.title()} reached your {action.upper()} target! It's now ${current_price}."))

    return messages

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

async def send_notifications():
    messages = check_alerts()
    for user_id, message in messages:
        await app.bot.send_message(chat_id=user_id, text=message)

async def add_favourite(update: Update, context: CallbackContext):
    try:
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /crypto-alerts <crypto_name>")
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
        await update.message.reply_text("You have no favourite cryptos yet! Use /crypto-alerts <crypto_name> to add one.")
    else:
        fav_list = "\n".join(f"- {fav[0].title()}" for fav in favs)
        await update.message.reply_text(f"⭐ Your Favourite Cryptos:\n{fav_list}")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cryptos", show_cryptos))
app.add_handler(CommandHandler("alert", set_alert))
app.add_handler(CommandHandler("alerts_buy", set_alert))
app.add_handler(CommandHandler("alerts_sell", set_alert))
app.add_handler(CommandHandler("crypto_alerts", add_favourite))
app.add_handler(CommandHandler("my_favourites", show_favourites))



# Start bot polling
if __name__ == "__main__":
    app.run_polling()
