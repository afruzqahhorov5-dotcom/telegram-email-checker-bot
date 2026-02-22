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
    print("🤖 Bot polling START...")
    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60,
                allowed_updates=["message", "callback_query"]
            )
        except Exception as e:
            print("❌ POLLING CRASH:", e)
            time.sleep(10)  # ← biroz ko‘proq kutamiz


if __name__ == "__main__":
    print("🚀 MAIN START")

    t = threading.Thread(target=run_bot, daemon=True)  # 🔥 MUHIM
    t.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
