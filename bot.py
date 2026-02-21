from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes,
    MessageHandler, filters
)

from flask import Flask
from threading import Thread

TOKEN = "8441883451:AAFVJ42P_EZs0CLCEb0SjiYYiwXrOQh-gzU"
BOOKING_URL = "https://t.me/Prilivi"

HINT_TEXT = (
    "Прочти свои образы самостоятельно:\n\n"
    "1) Первая комната «облаков» — это твоё мышление\n"
    "2) Вторая комната «дверь в сад» — это твои чувства\n"
    "3) Третья комната «игры» — это твоя воля (действия или бездействие)\n"
    "4) Четвёртая комната без названия — это твоя опора\n"
)

# ---- WEB PING (Render) ----
app_web = Flask(__name__)

@app_web.get("/health")
def health():
    return "ok", 200

def run_web():
    import os
    port = int(os.environ.get("PORT", "10000"))
    app_web.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
# ---------------------------


# --------- АНАЛИТИКА: запись в файл ----------
def log_answer(user_id, question, answer):
    with open("answers.txt", "a", encoding="utf-8") as f:
        f.write(f"{user_id} | {question} | {answer}\n")
# --------------------------------------------


# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Получить подсказку", callback_data="help")]]
    await update.message.reply_text(
        "Нажми кнопку ниже:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# --- кнопки ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Кнопка "Получить подсказку" -> вопрос 1
    if query.data == "help":
        log_answer(user_id, "START", "help_clicked")

        keyboard = [
            [InlineKeyboardButton("Да", callback_data="q1_yes")],
            [InlineKeyboardButton("Нет", callback_data="q1_no")],
            [InlineKeyboardButton("Свой ответ", callback_data="q1_custom")]
        ]
        await query.message.reply_text(
            HINT_TEXT + "\nУдалось ли тебе самостоятельно расшифровать свои образы?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Вопрос 1: Да/Нет -> вопрос 2
    elif query.data in ["q1_yes", "q1_no"]:
        log_answer(user_id, "Q1", query.data)

        keyboard = [
            [InlineKeyboardButton("Да", callback_data="q2_yes")],
            [InlineKeyboardButton("Частично", callback_data="q2_part")],
            [InlineKeyboardButton("Нет", callback_data="q2_no")]
        ]
        await query.message.reply_text(
            "Помогла ли самодиагностика разобраться?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Вопрос 1: свой ответ -> ждём текст
    elif query.data == "q1_custom":
        log_answer(user_id, "Q1", "custom_button")
        context.user_data["waiting_custom"] = "q1"
        await query.message.reply_text("Ок, напиши свой ответ текстом 👇")

    # Вопрос 2: Да/Частично -> вопрос 3
    elif query.data in ["q2_yes", "q2_part"]:
        log_answer(user_id, "Q2", query.data)

        keyboard = [
            [InlineKeyboardButton("Да", callback_data="q3_yes")],
            [InlineKeyboardButton("Нет", callback_data="q3_no")],
            [InlineKeyboardButton("Свой вариант", callback_data="q3_custom")]
        ]
        await query.message.reply_text(
            "Хочешь больше подобных техник на разные темы?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Вопрос 2: Нет -> уточнение нужна помощь?
    elif query.data == "q2_no":
        log_answer(user_id, "Q2", "q2_no")

        keyboard = [
            [InlineKeyboardButton("Мне нужна помощь", callback_data="need_help")],
            [InlineKeyboardButton("Мне не нужна помощь", callback_data="no_help")]
        ]
        await query.message.reply_text(
            "Хочешь, чтобы я помогла с расшифровкой?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Нужна помощь -> кнопка записи
    elif query.data == "need_help":
        log_answer(user_id, "HELP", "need_help")

        keyboard = [[InlineKeyboardButton("Запись на разбор", url=BOOKING_URL)]]
        await query.message.reply_text(
            "Ок. Нажми кнопку и напиши мне в личные сообщения: «нужен разбор самодиагностики».",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Не нужна помощь -> всё равно спросим про техники
    elif query.data == "no_help":
        log_answer(user_id, "HELP", "no_help")

        keyboard = [
            [InlineKeyboardButton("Да", callback_data="q3_yes")],
            [InlineKeyboardButton("Нет", callback_data="q3_no")],
            [InlineKeyboardButton("Свой вариант", callback_data="q3_custom")]
        ]
        await query.message.reply_text(
            "Ок 🙂 Тогда вопрос: хочешь больше подобных техник на разные темы?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Вопрос 3: Да/Нет -> финал
    elif query.data in ["q3_yes", "q3_no"]:
        log_answer(user_id, "Q3", query.data)

        await query.message.reply_text(
            "Спасибо! Сейчас я собираю отклик, чтобы понять, нужно ли людям больше таких техник на разные темы. "
            "Твой ответ очень помогает 🙌"
        )

    # Вопрос 3: свой вариант -> ждём текст
    elif query.data == "q3_custom":
        log_answer(user_id, "Q3", "custom_button")
        context.user_data["waiting_custom"] = "q3"
        await query.message.reply_text("Ок, напиши свой вариант текстом 👇")


# --- текстовые ответы (для 'Свой ответ/вариант') ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting = context.user_data.get("waiting_custom")
    user_id = update.effective_user.id

    if waiting == "q1":
        context.user_data["waiting_custom"] = None
        log_answer(user_id, "Q1_TEXT", update.message.text)

        keyboard = [
            [InlineKeyboardButton("Да", callback_data="q2_yes")],
            [InlineKeyboardButton("Частично", callback_data="q2_part")],
            [InlineKeyboardButton("Нет", callback_data="q2_no")]
        ]
        await update.message.reply_text(
            "Спасибо! Помогла ли самодиагностика разобраться?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif waiting == "q3":
        context.user_data["waiting_custom"] = None
        log_answer(user_id, "Q3_TEXT", update.message.text)

        await update.message.reply_text(
            "Спасибо! Сейчас я собираю отклик, чтобы понять, нужно ли людям больше таких техник на разные темы. "
            "Твой ответ очень помогает 🙌"
        )


# --- запуск ---
def main():
    Thread(target=run_web, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
# ---- WEB PING (Render) ----
from flask import Flask
from threading import Thread
import os

app_web = Flask(__name__)

@app_web.get("/health")
def health():
    return "ok", 200

def run_web():
    port = int(os.environ.get("PORT", "10000"))
    app_web.run(host="0.0.0.0", port=port)
# ---------------------------
if __name__ == "__main__":
    main()