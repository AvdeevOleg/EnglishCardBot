import random
import psycopg2
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = 'Ваш токен Telegram_bot'
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []

# Подключение к базе данных
conn = psycopg2.connect(
    dbname='english_card_bot_new',
    user='new_user',
    password='11111',
    host='localhost'
)
cur = conn.cursor()


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


def generate_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*buttons)
    return markup


def create_new_buttons():
    global buttons
    buttons = []

    # Получить слово из базы данных
    cur.execute("SELECT target_word, translate_word FROM words WHERE user_id IS NULL ORDER BY RANDOM() LIMIT 1;")
    word = cur.fetchone()
    if word:
        target_word, translate = word
    else:
        target_word, translate = 'Peace', 'Мир'

    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)

    # Получить другие слова из базы данных
    cur.execute("SELECT target_word FROM words WHERE user_id IS NULL AND target_word != %s ORDER BY RANDOM() LIMIT 3;",
                (target_word,))
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

    return target_word, translate, others


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid,
                         "Привет 👋 Давай попрактикуемся в английском языке. Тренировки можешь проходить в удобном для себя темпе.")

    target_word, translate, others = create_new_buttons()
    markup = generate_markup()

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    target_word, translate, others = create_new_buttons()
    markup = generate_markup()

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        cur.execute("DELETE FROM words WHERE target_word = %s AND user_id = %s;", (target_word, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, f"Слово '{target_word}' успешно удалено!")


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    bot.set_state(message.from_user.id, MyStates.another_words, message.chat.id)
    bot.send_message(message.chat.id, "Введите новое слово в формате: слово - перевод")


@bot.message_handler(state=MyStates.another_words, content_types=['text'])
def save_new_word(message):
    try:
        target_word, translate_word = message.text.split(' - ')
        cur.execute("INSERT INTO words (target_word, translate_word, user_id) VALUES (%s, %s, %s);",
                    (target_word, translate_word, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, f"Слово '{target_word}' успешно добавлено!")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, используйте формат: слово - перевод")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺 {data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)

