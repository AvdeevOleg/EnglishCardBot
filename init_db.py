import psycopg2
from config import DB_CONFIG

# Функция для создания таблиц
def create_tables():
    commands = (
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
            rus VARCHAR(255) NOT NULL,
            eng VARCHAR(255) NOT NULL,
            user_id BIGINT DEFAULT NULL,
            CONSTRAINT fk_user
              FOREIGN KEY(user_id)
              REFERENCES users(id)
        )
        """
    )

    conn = None
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

# Функция для вставки начальных слов в базу данных
def insert_initial_words():
    words = [
        ('Красный', 'Red'),
        ('Синий', 'Blue'),
        ('Зелёный', 'Green'),
        ('Жёлтый', 'Yellow'),
        ('Я', 'I'),
        ('Ты', 'You'),
        ('Он', 'He'),
        ('Она', 'She'),
        ('Мы', 'We'),
        ('Они', 'They')
    ]

    sql_insert = "INSERT INTO words (rus, eng) VALUES (%s, %s)"
    conn = None
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.executemany(sql_insert, words)
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