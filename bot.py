import os
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "7760374335:AAG51ZJ-W5KjZLEnoEV_Ro_B6ytsB5s3Nw8"
OWNER_ID = 7940228784
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ====== СТАРТ ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне ZIP-файл, и я его проверю.")


# ====== ПОЛУЧЕНИЕ ZIP ======
async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.lower().endswith(".zip"):
        await update.message.reply_text("Я принимаю только .zip файлы.")
        return

    file = await doc.get_file()
    save_path = UPLOAD_DIR / doc.file_name
    await file.download_to_drive(str(save_path))

    await update.message.reply_text(f"✅ Файл {doc.file_name} сохранён.")


# ====== АДМИН-ПАНЕЛЬ ======
async def hftteam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к админ-панели.")
        return

    files = sorted(UPLOAD_DIR.glob("*.zip"))
    if not files:
        await update.message.reply_text("📂 В папке uploads нет файлов.")
        return

    buttons = []
    for f in files:
        buttons.append([InlineKeyboardButton(f.name, callback_data=f"get|{f.name}")])

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("📁 Список ZIP-файлов:", reply_markup=keyboard)


# ====== СКАЧИВАНИЕ ЧЕРЕЗ КНОПКИ ======
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id != OWNER_ID:
        await query.edit_message_text("⛔ Нет доступа.")
        return

    data = query.data
    if data.startswith("get|"):
        filename = data.split("|")[1]
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            await query.edit_message_text("Файл не найден.")
            return
        await context.bot.send_document(chat_id=user_id, document=file_path.open("rb"), filename=filename)
        await query.answer("📦 Отправляю файл...", show_alert=False)


# ====== ЗАПУСК ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hftteam", hftteam))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_zip))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("✅ Бот запущен. Жди команд в Telegram.")
    app.run_polling()


if __name__ == "__main__":
    main()
