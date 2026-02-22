import requests
import telebot
from telebot import types
import random
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN yo‘q")

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML",
    threaded=True,
    num_threads=4
)

# 🔥 webhookni majburan o‘chiramiz
try:
    bot.remove_webhook()
    print("✅ Webhook o‘chirildi")
except Exception as e:
    print("Webhook xato:", e)

# foydalanuvchi holati
user_waiting_email = set()

PROXY_LIST = [
    {"http": "socks5://185.46.212.88:1080", "https": "socks5://185.46.212.88:1080"},
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
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
        r = session.post(
            'https://api.fraudemail.com/email',
            json={'email': email},
            timeout=10
        )
        if r.status_code == 200 and 'valid_email' in r.text:
            return "✅ Haqiqiy"
        return "❌ Yaroqsiz"
    except Exception as e:
        print("check_email error:", e)
        return "❌ Tekshirib bo‘lmadi"

# ================= START =================
@bot.message_handler(commands=['start', 'help'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📧 Email tekshirish", callback_data="check"),
        types.InlineKeyboardButton("🌐 Proxy status", callback_data="proxy"),
    )

    bot.send_message(
        message.chat.id,
        "👋 <b>Email tekshirish botiga xush kelibsiz</b>\nTugmani bosing.",
        reply_markup=markup
    )

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    print("CALLBACK:", call.data)

    if call.data == "check":
        user_waiting_email.add(chat_id)
        bot.send_message(chat_id, "📧 Email yuboring:")

    elif call.data == "proxy":
        bot.send_message(chat_id, f"🌐 Proxy: {len(PROXY_LIST)} ta")

# ================= EMAIL =================
@bot.message_handler(content_types=['text'])
def email_handler(message):
    chat_id = message.chat.id
    text = message.text.strip()
    print("MSG:", text)

    if chat_id not in user_waiting_email:
        return

    if '@' not in text:
        bot.send_message(chat_id, "❌ Noto'g'ri email!")
        return

    user_waiting_email.discard(chat_id)

    status = bot.send_message(chat_id, f"📧 {text} tekshirilmoqda...")
    result = check_email(text)

    bot.edit_message_text(
        f"{result}\n\nEmail: {text}",
        chat_id=chat_id,
        message_id=status.message_id
    )
