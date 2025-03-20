import telebot
from db import *
from dotenv import load_dotenv
from ocr import ocr_image, questions_list
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

users = {}  # Тимчасове збереження ID сесій


@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Зареєструватися"))
    markup.add(KeyboardButton("Увійти"))
    bot.send_message(message.chat.id, "Вітаю! Оберіть дію:", reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == "Зареєструватися")
def register(message):
    bot.send_message(message.chat.id, "Введіть новий нікнейм:")
    bot.register_next_step_handler(message, get_username)


def get_username(message):
    username = message.text
    bot.send_message(message.chat.id, "Тепер введіть пароль:")
    bot.register_next_step_handler(message, lambda msg: save_user(msg, username))


def save_user(message, username):
    password = message.text
    if register_user(username, password):
        bot.send_message(message.chat.id, "✅ Реєстрація успішна! Тепер увійдіть у свій акаунт.")
    else:
        bot.send_message(message.chat.id, "❌ Такий нік вже існує. Спробуйте інший.")


@bot.message_handler(func=lambda msg: msg.text == "Увійти")
def login(message):
    bot.send_message(message.chat.id, "Введіть ваш нікнейм:")
    bot.register_next_step_handler(message, check_username)


def check_username(message):
    username = message.text
    bot.send_message(message.chat.id, "Тепер введіть пароль:")
    bot.register_next_step_handler(message, lambda msg: verify_user(msg, username))


def verify_user(message, username):
    password = message.text
    user_id = login_user(username, password)
    if user_id:
        users[message.chat.id] = user_id
        bot.send_message(message.chat.id, """
                    Привіт! Ось команди для бота (варто закріпити в чаті для зручності) ✍️
                    
                    /start – почати, отакої, вже почали!
                    /photo – надіслати фото з якого запишуться питання (по одному ! )
                    /add – написати питання вручну
                    /random – отримати випадкове питання!
                    /list – переглянути всііііі питання
                    /delete_all – оніі, видалити всі питання…
""")
    else:
        bot.send_message(message.chat.id, "❌ Невірні дані! Спробуйте ще раз.")


@bot.message_handler(commands=['add'])
def add_question_handler(message):
    if message.chat.id in users:
        bot.send_message(message.chat.id, "Напишіть питання для додавання:")
        bot.register_next_step_handler(message, save_question)
    else:
        bot.send_message(message.chat.id, "Спочатку увійдіть у систему!")


def save_question(message):
    user_id = users[message.chat.id]
    add_question(user_id, message.text)
    bot.send_message(message.chat.id, "✅ Питання додано!")


@bot.message_handler(commands=['random'])
def random_question_handler(message):
    if message.chat.id in users:
        user_id = users[message.chat.id]
        question = get_random_question(user_id)
        bot.send_message(message.chat.id, question if question else "❌ У вас немає питань!")
    else:
        bot.send_message(message.chat.id, "Спочатку увійдіть у систему!")


@bot.message_handler(commands=['list'])
def list_questions_handler(message):
    if message.chat.id in users:
        user_id = users[message.chat.id]
        questions = get_all_questions(user_id)
        bot.send_message(message.chat.id, "\n".join(questions) if questions else "❌ У вас немає питань!")
    else:
        bot.send_message(message.chat.id, "Спочатку увійдіть у систему!")


@bot.message_handler(commands=['delete_all'])
def delete_all_questions_handler(message):
    if message.chat.id in users:
        user_id = users[message.chat.id]
        delete_all_questions(user_id)
        bot.send_message(message.chat.id, "✅ Усі питання видалено!")
    else:
        bot.send_message(message.chat.id, "Спочатку увійдіть у систему!")


def create_language_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("🇺🇦 Українська"))
    markup.add(KeyboardButton("🇬🇧 English"))
    return markup


@bot.message_handler(commands=['photo'])
def photo_handler(message):
    if message.chat.id in users:
        # Запитуємо мову
        bot.send_message(message.chat.id, "Оберіть мову тексту на зображенні: 🇺🇦 Українська або 🇬🇧 English",
                         reply_markup=create_language_markup())
        # Перехід до наступного кроку
        bot.register_next_step_handler(message, lambda msg: process_photo_language(msg, message))
    else:
        bot.send_message(message.chat.id, "Спочатку увійдіть у систему!")


def process_photo_language(message, original_message):
    lang = 'ukr' if message.text == "🇺🇦 Українська" else 'eng'
    user_id= users[original_message.chat.id]
    # Далі чекаємо на фото
    bot.send_message(message.chat.id, "Тепер надішліть фото з текстом.")
    bot.register_next_step_handler(message, lambda msg: handle_photo_with_language(msg, original_message, lang))


def handle_photo_with_language(message, original_message, lang):
    # Отримуємо фото
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_path = f"temp_{original_message.chat.id}.jpg"

        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Розпізнавання тексту на фото
        text = ocr_image(image_path, lang=lang)
        os.remove(image_path)

        # Отримуємо список питань і додаємо їх до БД
        questions = questions_list(text)
        if questions:
            for q in questions:
                user_id = users[message.chat.id]
                add_question(user_id, q)
            bot.send_message(original_message.chat.id, f"✅ Додано {len(questions)} питань із зображення!")
        else:
            bot.send_message(original_message.chat.id, "❌ Не валося розпізнати питання!")
    else:
        bot.send_message(message.chat.id, "Будь ласка, надішліть фото.")


if __name__ == "__main__":
    init_db()
    bot.polling(none_stop=True)