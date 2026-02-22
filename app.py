from flask import Flask
import os
import threading
import time
from bot import bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti!", 200


def run_bot():
    print("🤖 Bot ishga tushdi...")
    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )
        except Exception as e:
            print("❌ BOT CRASH:", e)
            time.sleep(5)


# 🔥 MUHIM: threadni main ichida ishga tushiramiz
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    print("🚀 Bot thread start qilindi")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
