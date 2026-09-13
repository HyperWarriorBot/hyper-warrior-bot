import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

# Users who have successfully purchased premium
premium_users = set()


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
        "✍️ Writing tools\n"
        "📄 CV & document assistance\n"
        "🖼️ AI image generation\n"
        "⭐ Premium services\n\n"
        "Choose a service below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai":
        await query.message.reply_text(
            "🤖 AI Assistant\n\n"
            "Send me a question and I'll help you.\n\n"
            "Free users will have limited access. ⭐ Premium users will get more."
        )

    elif query.data == "premium":
        keyboard = [
            [InlineKeyboardButton("⭐ Buy Premium — 100 Stars", callback_data="buy")]
        ]

        await query.message.reply_text(
            "⭐ HYPER WARRIOR PREMIUM\n\n"
            "Premium gives you access to more powerful features.\n\n"
            "💎 Premium — 100 Telegram Stars\n"
            "📅 30 days access\n"
            "🤖 AI Assistant\n"
            "✍️ Writing tools\n"
            "📄 CV assistance\n\n"
            "Tap below to purchase:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "buy":
        await send_payment(query.message)

    elif query.data == "account":
        user_id = query.from_user.id

        if user_id in premium_users:
            status = "⭐ Premium ACTIVE"
        else:
            status = "🆓 Free plan"

        await query.message.reply_text(
            f"👤 Your Hyper Warrior Account\n\n"
            f"Status: {status}\n\n"
            f"Use /start to return to the main menu."
        )

    elif query.data == "help":
        await query.message.reply_text(
            "ℹ️ Hyper Warrior Help\n\n"
            "Use /start to open the main menu.\n"
            "Choose AI Assistant to use the bot.\n"
            "Choose Premium to upgrade your account."
        )


async def send_payment(message):
    await message.reply_invoice(
        title="Hyper Warrior Premium",
        description="30 days of Hyper Warrior Premium access.",
        payload="hyper_warrior_premium_30_days",
        currency="XTR",
        prices=[],
    )


async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query

    await query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    premium_users.add(user_id)

    await update.message.reply_text(
        "🎉 PAYMENT SUCCESSFUL!\n\n"
        "⭐ Your Hyper Warrior Premium access is now active.\n\n"
        "Thank you for supporting Hyper Warrior! 🚀"
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        await update.message.reply_text(
            "🤖 Hyper Warrior received your message!\n\n"
            "The AI engine will be connected next. 🚀"
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    print("Hyper Warrior is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
