import random
import psycopg2
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from config import DB_CONFIG, TOKEN

print('Запуск Telegram бота...')

state_storage = StateMemoryStorage()
bot = TeleBot(TOKEN, state_storage=state_storage)

# Подключение к базе данных
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()

def user_exists(uid):
    cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (uid,))
    return cur.fetchone() is not None

def get_user_id(uid):
    cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (uid,))
    user = cur.fetchone()
    return user[0] if user else None

def get_user_step(uid):
    cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (uid,))
    user = cur.fetchone()
    if user:
        return user[0]
    else:
        bot.send_message(uid, "Пожалуйста, используйте команду /start для начала.")
        return None

def generate_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons)
    return markup

def create_new_buttons(uid):
    global buttons
    buttons = []

    # Получить случайное слово из базы данных (общие или принадлежащие пользователю)
    cur.execute("""
        SELECT rus, eng FROM words
        WHERE user_id IS NULL OR user_id = %s
        ORDER BY RANDOM() LIMIT 1;
    """, (uid,))
    word = cur.fetchone()
    if word:
        rus, eng = word
    else:
        rus, eng = 'Мир', 'Peace'

    target_word_btn = types.KeyboardButton(eng)
    buttons.append(target_word_btn)

    # Получить другие слова из базы данных (общие или принадлежащие пользователю)
    cur.execute("""
        SELECT eng FROM words
        WHERE (user_id IS NULL OR user_id = %s) AND eng != %s
        ORDER BY RANDOM() LIMIT 3;
    """, (uid, eng))
    others = cur.fetchall()
    others = [row[0] for row in others]
    if len(others) < 3:
        others.extend(['Green', 'White', 'Hello'])  # Резервный вариант

    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)

    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    return rus, eng, others

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    cur.execute("SELECT id FROM users WHERE telegram_id = %s;", (uid,))
    user = cur.fetchone()
    if not user:
        cur.execute(
            "INSERT INTO users (telegram_id, username, first_name, last_name) VALUES (%s, %s, %s, %s)",
            (uid, message.chat.username, message.chat.first_name, message.chat.last_name)
        )
        conn.commit()
    bot.send_message(uid,
                     "Привет! 👋 Давай попрактикуемся в английском языке. Тренировки можешь проходить в удобном для себя темпе.")
    create_cards(message)

@bot.message_handler(commands=['cards'])
def create_cards(message):
    uid = message.chat.id
    target_word, translate, others = create_new_buttons(uid)
    markup = generate_markup()

    greeting = f"Выбери перевод слова:\n🇷🇺 {target_word}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others

@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    bot.send_message(message.chat.id, "Введите слово на английском, которое хотите удалить:")
    bot.set_state(message.from_user.id, MyStates.translate_word, message.chat.id)

@bot.message_handler(state=MyStates.translate_word)
def process_delete_word(message):
    uid = message.chat.id
    word_to_delete = message.text.strip()
    user_id = get_user_id(uid)
    cur.execute("DELETE FROM words WHERE eng = %s AND user_id = %s;", (word_to_delete, user_id))
    conn.commit()
    if cur.rowcount > 0:
        bot.send_message(message.chat.id, f"Слово '{word_to_delete}' успешно удалено!")
    else:
        bot.send_message(message.chat.id, "Вы можете удалить только свои слова.")
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    bot.set_state(message.from_user.id, MyStates.another_words, message.chat.id)
    bot.send_message(message.chat.id,
                     "Введите слово на русском и его перевод на английский через запятую (например, собака,dog):")

@bot.message_handler(state=MyStates.another_words)
def process_add_word(message):
    try:
        uid = message.chat.id
        rus, eng = message.text.split(',')
        rus = rus.strip()
        eng = eng.strip()

        # Получаем id пользователя
        user_id = get_user_id(uid)
        if user_id is None:
            bot.send_message(message.chat.id, "Пожалуйста, используйте команду /start для начала.")
            return

        # Теперь добавляем слово
        cur.execute("INSERT INTO words (rus, eng, user_id) VALUES (%s, %s, %s);", (rus, eng, user_id))
        conn.commit()
        bot.send_message(message.chat.id, f"Слово '{rus} - {eng}' успешно добавлено!")
        bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении слова. Пожалуйста, попробуйте снова.")
        print(e)

@bot.message_handler(state=MyStates.target_word)
def check_translation(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        translate_word = data['translate_word']
        other_words = data['other_words']

    if message.text == translate_word:
        bot.send_message(message.chat.id, "Правильно! 🎉")
    else:
        bot.send_message(message.chat.id, f"Неправильно. Правильный ответ: {translate_word}")

# Запуск бота
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling()




