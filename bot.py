import logging
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== SOZLAMALAR ==================
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8410700261:AAHr997ntSujjgECJdWTCxZPziLAhMxuY7I"
ADMIN_ID = 6417772942

REQUIRED_CHANNEL = "@furry_uz_ff"
REQUIRED_CHANNEL_LINK = "https://t.me/furry_uz_ff"

CARD_NUMBER = "9860 6067 5181 1385"
CARD_OWNER = "A/D"

# ================== DATA ==================
balances = {}
pending_topups = {}

PRODUCTS = {
    "panel30": {
        "name": "🎯 30% Panel",
        "price": 10000,
        "ban": "0% ban",
        "desc": "📌 30% hedshot\n⚡ Yengil va tez",
        "channel": "https://t.me/+FSu_4yZ1CRplNWEy",
    },
    "poco": {
        "name": "🔥 Poco Redmi 100% Headshot",
        "price": 50000,
        "ban": "50/50",
        "desc": "🎯 Kuchli hedshot\n📹 Video qo‘llanma bor",
        "channel": "https://t.me/+PtwQWwC6nqs3OGZi",
    },
    "vzlom": {
        "name": "💎 Free Fire Vzlom Menu",
        "price": 35000,
        "ban": "0% ban",
        "desc": "💰 VIP / Almaz\n⚠️ Xavf yo‘q",
        "channel": "https://t.me/+PtwQWwC6nqs3OGZi",
    },
    "skin": {
        "name": "🎨 Skin Hack",
        "price": 7000,
        "ban": "0% ban",
        "desc": "🧥 Barcha skinlar ochiladi\n🔒 Xavfsiz",
        "channel": "https://t.me/+Kx14tGtORjxlMzdi",
    },
}

# ================== KANAL TEKSHIRISH ==================
async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balances.setdefault(user_id, 0)

    if not await check_sub(update, context):
        text = "🔒 Botdan foydalanish uchun kanalga obuna bo‘ling!"
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga o‘tish", url=REQUIRED_CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")],
        ]
    else:
        text = (
            "👋 Assalomu alaykum!\n\n"
            "🎮 Free Fire uchun eng zo‘r chitlar!\n"
            "⬇️ Menyudan tanlang:"
        )
        keyboard = [
            [InlineKeyboardButton("🛒 Mahsulotlar", callback_data="products")],
            [InlineKeyboardButton("💰 Hisobim", callback_data="balance")],
            [InlineKeyboardButton("➕ Hisob to‘ldirish", callback_data="topup")],
        ]

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ================== BUTTONLAR ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = q.from_user.id
    balances.setdefault(user_id, 0)

    if data == "check_sub":
        await start(update, context)

    elif data == "products":
        keyboard = [
            [InlineKeyboardButton(p["name"], callback_data=f"prod_{k}")]
            for k, p in PRODUCTS.items()
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back")])
        await q.message.edit_text("🛒 Mahsulotlar:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("prod_"):
        key = data.replace("prod_", "")
        p = PRODUCTS[key]
        text = (
            f"{p['name']}\n\n"
            f"{p['desc']}\n\n"
            f"🚫 Ban: {p['ban']}\n"
            f"💰 Narx: {p['price']} so‘m"
        )
        keyboard = [
            [InlineKeyboardButton("🛒 Sotib olish", callback_data=f"buy_{key}")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="products")],
        ]
        await q.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("buy_"):
        key = data.replace("buy_", "")
        p = PRODUCTS[key]

        if balances[user_id] < p["price"]:
            await q.message.reply_text("❌ Mablag‘ yetarli emas")
            return

        balances[user_id] -= p["price"]
        await q.message.reply_text(
            f"✅ Xarid qilindi!\n\n"
            f"📢 Yuklab olish shu kanalda:\n{p['channel']}"
        )

    elif data == "balance":
        await q.message.reply_text(f"💰 Balansingiz: {balances[user_id]} so‘m")

    elif data == "topup":
        context.user_data["await_amount"] = True
        await q.message.reply_text("💳 Qancha summa kiritasiz?")

    elif data == "back":
        await start(update, context)

    elif data.startswith("confirm_"):
        uid = int(data.replace("confirm_", ""))
        if uid in pending_topups:
            balances[uid] += pending_topups[uid]["amount"]
            del pending_topups[uid]
            await q.message.reply_text("✅ To‘lov tasdiqlandi")
            await context.bot.send_message(uid, "✅ Hisobingiz to‘ldirildi")

    elif data.startswith("reject_"):
        uid = int(data.replace("reject_", ""))
        pending_topups.pop(uid, None)
        await q.message.reply_text("❌ To‘lov rad etildi")

# ================== MATN ==================
async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("await_amount"):
        try:
            amount = int(update.message.text)
        except:
            await update.message.reply_text("❌ Faqat raqam kiriting")
            return

        context.user_data["await_amount"] = False
        context.user_data["await_photo"] = True
        context.user_data["amount"] = amount

        await update.message.reply_text(
            f"💳 Karta:\n{CARD_NUMBER}\n{CARD_OWNER}\n\n"
            f"{amount} so‘m to‘lab, chek rasmini yuboring"
        )

# ================== RASM ==================
async def photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("await_photo"):
        context.user_data["await_photo"] = False
        amount = context.user_data["amount"]
        photo = update.message.photo[-1].file_id

        pending_topups[user_id] = {"amount": amount, "photo": photo}

        keyboard = [
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user_id}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}"),
            ]
        ]

        await context.bot.send_photo(
            ADMIN_ID,
            photo,
            caption=f"💰 To‘lov\n👤 {user_id}\n💵 {amount}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        await update.message.reply_text("⏳ Admin tekshiryapti...")

# ================== MAIN ==================
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texts))
    app.add_handler(MessageHandler(filters.PHOTO, photos))

    print("✅ Bot ishga tushdi")
    app.run_polling()

if __name__ == "__main__":
    main()

    

