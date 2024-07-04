import psycopg2
from psycopg2 import sql
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

def get_random_word():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, rus, eng FROM words ORDER BY RANDOM() LIMIT 1")
    word = cur.fetchone()
    cur.close()
    conn.close()
    return word

def add_user_word(user_id, word_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_words (user_id, word_id) VALUES (%s, %s)",
        (user_id, word_id)
    )
    conn.commit()
    cur.close()
    conn.close()

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
