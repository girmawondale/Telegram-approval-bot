from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler,
    CallbackQueryHandler, filters
)
from flask import Flask
from threading import Thread

# === Configuration ===
BOT_TOKEN = "8123619470:AAHrkX0FGTUloy8v3EJT3P334U86F6bwG_I"
GROUP_ID = -1002547554880
ADMIN_ID = 697616131

# === Flask App to Keep Replit Alive ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Handlers ===
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received message: {update.message.text}")

    user = update.effective_user
    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    message_text = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve|{full_name}|{message_text}"),
            InlineKeyboardButton("❌ Reject", callback_data="reject")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📝 New submission from {full_name}:\n\n{message_text}",
        reply_markup=reply_markup
    )

    await update.message.reply_text("✅ Your message has been sent to the admin for approval.")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id != ADMIN_ID:
        await query.answer("⛔ You are not authorized to approve.", show_alert=True)
        return

    data = query.data

    if data.startswith("approve|"):
        _, full_name, message_text = data.split("|", 2)
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"📢 Approved message from {full_name}:\n\n{message_text}"
        )
        await query.edit_message_text("✅ Message approved and posted.")
    elif data == "reject":
        await query.edit_message_text("❌ Submission rejected.")

# === Run Both Flask and Bot ===
def main():
    Thread(target=run_flask).start()

    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    app_bot.add_handler(CallbackQueryHandler(handle_buttons))

    print("🤖 Bot is running...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
