import logging
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
BOT_TOKEN = "8410700261:AAHr997ntSujjgECJdWTCxZPziLAhMxuY7I"
ADMIN_ID = 6417772942

# 🔒 MAJBURIY KANAL
REQUIRED_CHANNEL = "@furry_uz_ff"

# 💳 KARTA
CARD_NUMBER = "9860 6067 5181 1385"
CARD_OWNER = "A/D"

# ================== DATA ==================
balances = {}
pending_topups = {}

# ================== MAHSULOTLAR ==================
PRODUCTS = {
    "poco": {
        "name": "🎯 Poco Redmi 100% Headshot",
        "price": 50000,
        "ban": "⚠️ 50/50",
        "desc": "🔥 100% headshot\n🛡 95% bezban\n🎥 Video qo‘llanma bor",
        "channel": "https://t.me/+PtwQWwC6nqs3OGZi",
    },
    "wallhack": {
        "name": "👁 WallHack",
        "price": 20000,
        "ban": "⚠️ 50/50",
        "desc": "👥 Odamlarni ko‘rsatadi\n🛡 60% bezban",
        "channel": "https://t.me/+PtwQWwC6nqs3OGZi",
    },
    "panel30": {
        "name": "📊 30% Panel",
        "price": 10000,
        "ban": "✅ 0%",
        "desc": "🎯 30% headshot\n💸 Arzon va yengil",
        "channel": "https://t.me/+FSu_4yZ1CRplNWEy",
    },
    "vzlom": {
        "name": "💎 Free Fire Vzlom",
        "price": 35000,
        "ban": "✅ 0%",
        "desc": "💎 Almaz + VIP\n🚀 Ishlaydi",
        "channel": "https://t.me/+PtwQWwC6nqs3OGZi",
    },
    "skin": {
        "name": "🎭 Skin Hack",
        "price": 25000,
        "ban": "✅ 0%",
        "desc": "🎨 Skinlar ochiladi\n🔐 Xavfsiz",
        "channel": "https://t.me/+Kx14tGtORjxlMzdi",
    },
}

# ================== MAJBURIY OBUNA TEKSHIRISH ==================
async def check_sub(user_id, bot):
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balances.setdefault(user_id, 0)

    if not await check_sub(user_id, context.bot):
        keyboard = [[
            InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{REQUIRED_CHANNEL.replace('@','')}"),
            InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
        ]]
        await update.message.reply_text(
            "🔒 Botdan foydalanish uchun kanalga obuna bo‘ling!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    text = (
        "👋 Assalomu alaykum!\n\n"
        "🔥 Free Fire uchun chitlar do‘koni\n"
        "⬇️ Kerakli bo‘limni tanlang:"
    )

    keyboard = [
        [InlineKeyboardButton("🛒 Mahsulotlar", callback_data="products")],
        [InlineKeyboardButton("💰 Hisobim", callback_data="balance")],
        [InlineKeyboardButton("➕ Hisob to‘ldirish", callback_data="topup")],
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ================== BUTTONLAR ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    balances.setdefault(user_id, 0)

    if q.data == "check_sub":
        if await check_sub(user_id, context.bot):
            await start(update, context)
        else:
            await q.message.reply_text("❌ Avval kanalga obuna bo‘ling!")

    elif q.data == "products":
        keyboard = [
            [InlineKeyboardButton(p["name"], callback_data=f"prod_{k}")]
            for k, p in PRODUCTS.items()
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back")])
        await q.message.reply_text("🛒 Mahsulotlar:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif q.data.startswith("prod_"):
        key = q.data.replace("prod_", "")
        p = PRODUCTS[key]
        text = (
            f"{p['name']}\n\n"
            f"{p['desc']}\n\n"
            f"🚫 Ban ehtimoli: {p['ban']}\n"
            f"💰 Narx: {p['price']} so‘m"
        )
        keyboard = [
            [InlineKeyboardButton("🛒 Sotib olish", callback_data=f"buy_{key}")],
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="products")],
        ]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif q.data.startswith("buy_"):
        key = q.data.replace("buy_", "")
        p = PRODUCTS[key]
        if balances[user_id] < p["price"]:
            await q.message.reply_text("❌ Mablag‘ yetarli emas!")
            return
        balances[user_id] -= p["price"]
        await q.message.reply_text(f"✅ Sotib olindi!\n📢 Kanal: {p['channel']}")

    elif q.data == "balance":
        await q.message.reply_text(f"💰 Balans: {balances[user_id]} so‘m")

    elif q.data == "topup":
        context.user_data["await_amount"] = True
        await q.message.reply_text("💳 Qancha summa kiritasiz?")

    elif q.data == "back":
        await start(update, context)

# ================== TEXT ==================
async def texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("await_amount"):
        amount = int(update.message.text)
        context.user_data.clear()
        context.user_data["await_photo"] = True
        context.user_data["amount"] = amount
        await update.message.reply_text(
            f"💳 {CARD_NUMBER}\n👤 {CARD_OWNER}\n\n"
            f"{amount} so‘m to‘lab, chek rasmini yuboring 📸"
        )

# ================== PHOTO ==================
async def photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("await_photo"):
        user_id = update.effective_user.id
        amount = context.user_data["amount"]
        photo = update.message.photo[-1].file_id
        pending_topups[user_id] = {"amount": amount}

        keyboard = [[
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}")
        ]]

        await context.bot.send_photo(
            ADMIN_ID,
            photo,
            caption=f"💰 To‘lov\n👤 {user_id}\n💵 {amount} so‘m",
            reply_markup=InlineKeyboardMarkup(keyboard)
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



