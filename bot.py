import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Если токены не заданы — выходим с ошибкой
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не задан!")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN не задан!")

# Инициализация клиента Hugging Face
client = InferenceClient(token=HF_TOKEN)

# Модель для диалогов
TEXT_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Создание клавиатуры
keyboard = ReplyKeyboardMarkup(
    [["Дай мотивацию!", "Помоги с задачей"]],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Мотивационный Бот! 🌟\n"
        "Я создан, чтобы вдохновлять тебя и помогать справляться с трудностями. "
        "Напиши, что тебя волнует (например, 'Я устал' или 'Как быть продуктивнее?'), "
        "и я дам персонализированный совет. Или используй кнопки ниже для быстрого вдохновения!",
        reply_markup=keyboard
    )

# Обработчик текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "Дай мотивацию!":
        prompt = "Дай мотивирующую цитату или совет на русском языке, чтобы вдохновить человека двигаться вперёд."
    elif user_text == "Помоги с задачей":
        prompt = "Дай практический совет на русском языке, как эффективно справиться с задачей или организовать работу."
    else:
        prompt = f"Пользователь написал: '{user_text}'. Дай мотивирующий и полезный ответ на русском языке, учитывая контекст. Если пользователь выразил проблему, предложи решение. Если запрос общий, дай вдохновляющий совет."

    try:
        response = client.chat_completion(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Ой, что-то пошло не так: {e}. Попробуй ещё раз!")

# Основная функция
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Render дает порт через переменную PORT, но мы используем polling
    port = int(os.environ.get("PORT", 8080))
    app.run_polling()

if __name__ == '__main__':
    main()
