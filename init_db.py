import psycopg2
from config import DB_CONFIG


# Функция для создания таблиц
def create_tables():
    команды = (
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS words (
            id SERIAL PRIMARY KEY,
            target_word VARCHAR(255) NOT NULL,
            translate_word VARCHAR(255) NOT NULL,
            user_id BIGINT DEFAULT NULL
        )
        """
    )

    conn = None
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        for команда in команды:
            cur.execute(команда)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# Функция для вставки начальных слов в базу данных
def insert_initial_words():
    слова = [
        ('Red', 'Красный'),
        ('Blue', 'Синий'),
        ('Green', 'Зелёный'),
        ('Yellow', 'Жёлтый'),
        ('I', 'Я'),
        ('You', 'Ты'),
        ('He', 'Он'),
        ('She', 'Она'),
        ('We', 'Мы'),
        ('They', 'Они')
    ]

    sql_insert = "INSERT INTO words (target_word, translate_word) VALUES (%s, %s)"
    conn = None
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.executemany(sql_insert, слова)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# Основная функция для выполнения всех действий
if __name__ == '__main__':
    create_tables()
    insert_initial_words()
    print("Таблицы созданы и начальные данные вставлены")
