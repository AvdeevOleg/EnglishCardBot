import psycopg2
from psycopg2 import sql
from config import DB_CONFIG
import psycopg2

def connect_to_db():
    conn = psycopg2.connect(
        database="english_card_bot",
        user="new_user",
        password="11111",
        host="localhost",
        port="5432",
        client_encoding="UTF8"
    )
    return conn

def get_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )


def create_user(username, first_name, last_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, first_name, last_name) VALUES (%s, %s, %s) RETURNING user_id",
        (username, first_name, last_name)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id


def get_random_word():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT word, translation FROM words ORDER BY RANDOM() LIMIT 1")
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
        "SELECT words.word, words.translation FROM words JOIN user_words ON words.word_id = user_words.word_id WHERE user_words.user_id = %s",
        (user_id,)
    )
    words = cur.fetchall()
    cur.close()
    conn.close()
    return words
