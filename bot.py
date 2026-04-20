from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8504633507:AAGVHSJO-9z0S0a3JY91kmLrJawxnOD2JOY"
CHANNEL_USERNAME = "@TWIXER_MUSIC"
FILE_PATH = "басс — копия.zip"
FILE_CAPTION = "🎵 Вот ваш драм кит! Спасибо за подписку на TWIXER!"

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME, 
            user_id=user_id
        )
        
        if member.status in ['left', 'kicked']:
            return False
        else:
            return True
            
    except TelegramError as e:
        print(f"Ошибка проверки: {e}")
        return False

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔔 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("📥 Получить ДК", callback_data="get_file")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_subscription_reminder_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔔 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("🔄 Проверить подписку", callback_data="check_again")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        f"🎵 Чтобы получить драм кит, подпишись на {CHANNEL_USERNAME}\n\n"
        f"👇 Кнопки внизу:"
    )
    
    await update.message.reply_text(text=welcome_text, reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "get_file":
        is_subscribed = await check_subscription(user_id, context)
        
        if is_subscribed:
            try:
                with open(FILE_PATH, 'rb') as file:
                    await context.bot.send_document(
                        chat_id=user_id,
                        document=file,
                        caption=FILE_CAPTION
                    )
                await query.edit_message_text(text="✅ Файл отправлен!", reply_markup=None)
            except FileNotFoundError:
                await query.edit_message_text(text="❌ Файл не найден.", reply_markup=None)
        else:
            await query.edit_message_text(
                text=f"❌ Вы НЕ подписаны на {CHANNEL_USERNAME}\n\nПодпишись и проверь:",
                reply_markup=get_subscription_reminder_keyboard()
            )
    
    elif data == "check_again":
        is_subscribed = await check_subscription(user_id, context)
        
        if is_subscribed:
            await query.edit_message_text(
                text="✅ Подписка есть! Жми получить:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📥 Получить ДК", callback_data="get_file")
                ]])
            )
        else:
            await query.edit_message_text(
                text=f"❌ Всё ещё не подписан на {CHANNEL_USERNAME}\n\nПодпишись и жми:",
                reply_markup=get_subscription_reminder_keyboard()
            )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
