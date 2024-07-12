import psycopg2
from config import DB_CONFIG

def connect_to_db():
    return psycopg2.connect(**DB_CONFIG)

def get_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )

def create_user(username, first_name, last_name, telegram_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, first_name, last_name, telegram_id) VALUES (%s, %s, %s, %s) RETURNING id",
        (username, first_name, last_name, telegram_id)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def user_exists(telegram_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE telegram_id = %s", (telegram_id,))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def get_random_word(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, rus, eng FROM words
        WHERE user_id IS NULL OR user_id = %s
        ORDER BY RANDOM() LIMIT 1
    """, (user_id,))
    word = cur.fetchone()
    cur.close()
    conn.close()
    return word

def add_user_word(telegram_id, username, first_name, last_name, rus, eng):
    # Проверяем, существует ли пользователь
    if not user_exists(telegram_id):
        # Если нет, создаем нового пользователя
        user_id = create_user(username, first_name, last_name, telegram_id)
    else:
        # Получаем id существующего пользователя
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        user_id = cur.fetchone()[0]
        cur.close()
        conn.close()

    # Добавляем слово
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO words (rus, eng, user_id) VALUES (%s, %s, %s) RETURNING id",
        (rus, eng, user_id)
    )
    word_id = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO user_words (user_id, word_id) VALUES (%s, %s)",
        (user_id, word_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return word_id

def delete_user_word(user_id, eng):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM words WHERE eng = %s AND user_id = %s RETURNING id",
        (eng, user_id)
    )
    deleted_id = cur.fetchone()
    if deleted_id:
        cur.execute(
            "DELETE FROM user_words WHERE word_id = %s AND user_id = %s",
            (deleted_id[0], user_id)
        )
        conn.commit()
    cur.close()
    conn.close()
    return deleted_id is not None

def get_user_words(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT words.rus, words.eng FROM words JOIN user_words ON words.id = user_words.word_id WHERE user_words.user_id = %s",
        (user_id,)
    )
    words = cur.fetchall()
    cur.close()
    conn.close()
    return words


