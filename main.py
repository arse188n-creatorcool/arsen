import json




import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
load_dotenv ()
# Токен вашего бота от @BotFather
TOKEN = "8985378072:AAGe091wlV3xY4MD1myvaxKXg_DCqJ_jArg"
DATA_FILE = "users_data.json"

TOKEN = os.environ.get('TOKEN')

# Загрузка данных из JSON
def load_data() -> dict:
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {}
  return {}


# Сохранение данных в JSON
def save_data(data: dict):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# Клавиатура с двумя кнопками
def get_main_keyboard() -> InlineKeyboardMarkup:
  keyboard = [
      [InlineKeyboardButton("Сохранить данные", callback_data="btn_save")],
      [InlineKeyboardButton("Имя", callback_data="btn_get")],
  ]
  return InlineKeyboardMarkup(keyboard)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "Привет! Выберите действие с помощью кнопок ниже:",
      reply_markup=get_main_keyboard(),
  )


# Обработка нажатий на инлайн-кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()  # Подтверждаем нажатие

  user_id = str(query.from_user.id)

  if query.data == "btn_save":
    # Сохраняем в контексте флаг, что ждем имя от этого пользователя
    context.user_data["waiting_for_name"] = True
    await query.message.reply_text("Пожалуйста, напишите ваше имя:")

  elif query.data == "btn_get":
    data = load_data()
    if user_id in data:
      saved_name = data[user_id]
      await query.message.reply_text(
          f"Сохраненное в JSON имя: <b>{saved_name}</b>", parse_mode="HTML"
      )
    else:
      await query.message.reply_text(
          "Вы еще не сохранили свое имя. Нажмите «Сохранить данные»."
      )


# Получение текста от пользователя (для сохранения имени)
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # Проверяем, ждем ли мы имя от этого пользователя
  if context.user_data.get("waiting_for_name"):
    user_id = str(update.message.from_user.id)
    name = update.message.text.strip()

    # Сохраняем в JSON
    data = load_data()
    data[user_id] = name
    save_data(data)

    # Сбрасываем флаг ожидания
    context.user_data["waiting_for_name"] = False

    await update.message.reply_text(
        f"Спасибо! Ваше имя <b>{name}</b> успешно сохранено.",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


def main():
  # Создаем приложение
  app = ApplicationBuilder().token(TOKEN).build()

  # Регистрируем обработчики
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_handler))
  app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
  )

  print("Бот запущен...")
  app.run_polling()


if __name__ == "__main__":
  main()