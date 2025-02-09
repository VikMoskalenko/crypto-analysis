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