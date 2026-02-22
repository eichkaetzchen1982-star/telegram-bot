import os
import threading
from flask import Flask

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

app = Flask(__name__)

@app.get("/")
def home():
    return "ok", 200


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я живой 🙂 Напиши /card")


async def card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здесь будет твоя логика карты Таро (пока тест).")


def run_telegram_bot():
    if not TOKEN:
        raise RuntimeError("TOKEN is not set in Environment Variables on Render")

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("card", card))

    # ВАЖНО: для v20 это правильный запуск
    application.run_polling()


if __name__ == "__main__":
    # запускаем телеграм-бота в отдельном потоке
    threading.Thread(target=run_telegram_bot, daemon=True).start()

    # а Flask держит порт для Render (Web Service)
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
