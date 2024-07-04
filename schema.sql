-- Схема базы данных для Telegram-бота по изучению английского языка

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,                -- Уникальный идентификатор пользователя
    telegram_id BIGINT UNIQUE NOT NULL,   -- Telegram ID пользователя
    username VARCHAR(255),                -- Имя пользователя в Telegram
    first_name VARCHAR(255),              -- Имя
    last_name VARCHAR(255)                -- Фамилия
);

-- Таблица слов
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,                -- Уникальный идентификатор слова
    rus VARCHAR(255) NOT NULL,            -- Слово на русском
    eng VARCHAR(255) NOT NULL,            -- Перевод слова на английский
    user_id BIGINT DEFAULT NULL,          -- Идентификатор пользователя, если слово добавлено пользователем
    CONSTRAINT fk_user
      FOREIGN KEY(user_id)
      REFERENCES users(id)
);

-- Таблица слов пользователей
CREATE TABLE IF NOT EXISTS user_words (
    user_id BIGINT NOT NULL,
    word_id BIGINT NOT NULL,
    PRIMARY KEY (user_id, word_id),
    CONSTRAINT fk_user
      FOREIGN KEY(user_id)
      REFERENCES users(id),
    CONSTRAINT fk_word
      FOREIGN KEY(word_id)
      REFERENCES words(id)
);

-- Вставка начальных данных
INSERT INTO words (rus, eng) VALUES
('Красный', 'Red'),
('Синий', 'Blue'),
('Зелёный', 'Green'),
('Жёлтый', 'Yellow'),
('Я', 'I'),
('Ты', 'You'),
('Он', 'He'),
('Она', 'She'),
('Мы', 'We'),
('Они', 'They');
