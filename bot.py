import requests
import telebot
from telebot import types
import time
import random
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===== TOKEN ENVdan olinadi =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN topilmadi!")
    raise SystemExit("BOT_TOKEN yo‘q")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# 🔥 ENG MUHIM — webhookni o‘chiramiz
try:
    bot.remove_webhook()
    print("✅ Webhook o‘chirildi")
except Exception as e:
    print("❌ Webhook o‘chirish xato:", e)

# 🔥 Foydalanuvchi holati
user_waiting_email = set()

# Proxy list
PROXY_LIST = [
    {"http": "socks5://185.46.212.88:1080", "https": "socks5://185.46.212.88:1080"},
    {"http": "socks5://103.149.162.194:1080", "https": "socks5://103.149.162.194:1080"},
    {"http": "http://45.155.86.131:8080", "https": "http://45.155.86.131:8080"},
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15",
]

# ================= SESSION =================
def create_session(use_proxy=False, proxy=None):
    session = requests.Session()
    retry_strategy = Retry(total=2, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    if use_proxy and proxy:
        session.proxies.update(proxy)

    session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
    return session

# ================= EMAIL CHECK =================
def check_email(email):
    try:
        session = create_session()
        response = session.post(
            'https://api.fraudemail.com/email',
            json={'email': email},
            timeout=10
        )
        if response.status_code == 200:
            if 'valid_email' in response.text:
                return True, "✅ Haqiqiy"
            else:
                return False, "❌ Yaroqsiz"
    except Exception as e:
        print("❌ Direct xato:", e)

    # 🔁 Proxy orqali
    for i, proxy in enumerate(PROXY_LIST):
        try:
            session = create_session(use_proxy=True, proxy=proxy)
            response = session.post(
                'https://api.fraudemail.com/email',
                json={'email': email},
                timeout=15
            )
            if response.status_code == 200:
                if 'valid_email' in response.text:
                    return True, f"✅ Haqiqiy (Proxy {i+1})"
                else:
                    return False, f"❌ Yaroqsiz (Proxy {i+1})"
        except Exception as e:
            print(f"❌ Proxy {i+1} xato:", e)
            continue

    return None, "❌ Ulanish imkonsiz"

# ================= START =================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📧 Email tekshirish", callback_data="check")
    btn2 = types.InlineKeyboardButton("🌐 Proxy status", callback_data="proxy")
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "👋 <b>Email tekshirish botiga xush kelibsiz</b>\nTugmani bosing.",
        reply_markup=markup
    )

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    print("CALLBACK:", call.data)  # 🔥 debug

    chat_id = call.message.chat.id

    if call.data == "check":
        user_waiting_email.add(chat_id)
        bot.send_message(chat_id, "📧 Email yuboring:")

    elif call.data == "proxy":
        bot.send_message(chat_id, f"🌐 Proxy: {len(PROXY_LIST)} ta")

# ================= EMAIL MESSAGE =================
@bot.message_handler(func=lambda message: True)
def check_email_handler(message):
    print("MSG:", message.text)  # 🔥 debug

    chat_id = message.chat.id

    if chat_id not in user_waiting_email:
        return

    email = message.text.strip()

    if '@' not in email:
        bot.send_message(chat_id, "❌ Noto'g'ri email format!")
        return

    user_waiting_email.discard(chat_id)

    status_msg = bot.send_message(
        chat_id,
        f"📧 {email} tekshirilmoqda..."
    )

    result, msg = check_email(email)

    try:
        bot.edit_message_text(
            f"{msg}\n\nEmail: {email}",
            chat_id=chat_id,
            message_id=status_msg.message_id
        )
    except Exception:
        bot.send_message(chat_id, f"{msg}\n\nEmail: {email}")
