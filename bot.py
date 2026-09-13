import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Users who have paid for premium during the current bot session
premium_users = set()


# ---------- TELEGRAM BOT ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤖 AI Assistant", callback_data="ai")],
        [InlineKeyboardButton("⭐ Premium", callback_data="premium")],
        [InlineKeyboardButton("👤 My Account", callback_data="account")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]

    await update.message.reply_text(
        "🚀 Welcome to Hyper Warrior!\n\n"
        "Your all-in-one digital assistant.\n\n"
        "🤖 AI Assistant\n"
        "✍️ Writing & content tools\n"
        "📄 CV & document assistance\n"
        "🖼️ AI image generation\n"
        "⭐ Premium services\n\n"
        "Start for free and upgrade when you need more power. 🔥",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai":
        await query.message.reply_text(
            "🤖 AI Assistant\n\n"
            "Send me a message and Hyper Warrior will process your request.\n\n"
            "🆓 Free access is limited.\n"
            "⭐ Upgrade to Premium for more access."
        )

    elif query.data == "premium":
        await send_premium_invoice(query.message)

    elif query.data == "account":
        user_id = query.from_user.id

        if user_id in premium_users:
            status = "⭐ Premium"
        else:
            status = "🆓 Free"

        await query.message.reply_text(
            f"👤 Your Hyper Warrior Account\n\n"
            f"Plan: {status}\n\n"
            "Use the Premium button to upgrade."
        )

    elif query.data == "help":
        await query.message.reply_text(
            "ℹ️ Hyper Warrior Help\n\n"
            "Use /start to open the main menu.\n"
            "Use /services to view services.\n"
            "Use /buy to purchase Premium.\n"
            "Use /account to check your account.\n\n"
            "Need help? Contact support."
        )


async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ Hyper Warrior Services\n\n"
        "🤖 AI Assistant\n"
        "✍️ Writing & Content\n"
        "📄 CV & Document Assistance\n"
        "🖼️ AI Image Generation\n"
        "⭐ Premium Access\n\n"
        "More services will be added soon. 🔥"
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_premium_invoice(update.message)


async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in premium_users:
        status = "⭐ Premium"
    else:
        status = "🆓 Free"

    await update.message.reply_text(
        f"👤 Your Account\n\n"
        f"Plan: {status}\n\n"
        "Thank you for using Hyper Warrior! 🔥"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Hyper Warrior Help\n\n"
        "/start - Open main menu\n"
        "/services - View services\n"
        "/buy - Buy Premium\n"
        "/account - View account\n"
        "/help - Get help"
    )


# ---------- TELEGRAM STARS PAYMENT ----------

async def send_premium_invoice(message):
    prices = [LabeledPrice("Hyper Warrior Premium - 30 days", 100)]

    await message.reply_invoice(
        title="⭐ Hyper Warrior Premium",
        description="Premium access to Hyper Warrior digital services for 30 days.",
        payload="hyper_warrior_premium_30_days",
        currency="XTR",
        prices=prices,
        provider_token="",
    )


async def precheckout_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.pre_checkout_query

    await query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    user_id = update.effective_user.id

    premium_users.add(user_id)

    await update.message.reply_text(
        "🎉 Payment successful!\n\n"
        "⭐ Your Hyper Warrior Premium access is now active.\n\n"
        "Thank you for supporting Hyper Warrior! 🔥"
    )


# ---------- NORMAL MESSAGES ----------

async def normal_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in premium_users:
        await update.message.reply_text(
            "⭐ Premium user detected!\n\n"
            "Your AI Assistant is ready. Send your request."
        )
    else:
        await update.message.reply_text(
            "🤖 Hyper Warrior received your message!\n\n"
            "The AI engine will be connected here next.\n\n"
            "⭐ Upgrade to Premium for full access."
        )


# ---------- RENDER WEB SERVER ----------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hyper Warrior is running")

    def log_message(self, format, *args):
        return


def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


# ---------- START BOT ----------

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("services", services))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("account", account))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(
        PreCheckoutQueryHandler(precheckout_callback)
    )

    app.add_handler(
        MessageHandler(
            filters.SUCCESSFUL_PAYMENT,
            successful_payment
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            normal_message
        )
    )

    print("Hyper Warrior is running...")

    threading.Thread(
        target=start_web_server,
        daemon=True
    ).start()

    app.run_polling()


if __name__ == "__main__":
    main()
