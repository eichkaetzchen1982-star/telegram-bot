import os
import threading

from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN environment variable is missing")

app = Flask(__name__)

@app.get("/")
def health():
    return "ok", 200


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Бот запущен ✅")


def run_telegram_bot() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_cmd))
    application.run_polling()


if __name__ == "__main__":
    # запускаем Telegram-бота в фоне
    t = threading.Thread(target=run_telegram_bot, daemon=True)
    t.start()

    # Flask должен слушать порт, который даёт Render
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
