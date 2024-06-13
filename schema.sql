-- Схема базы данных для Telegram-бота по изучению английского языка

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,       -- Уникальный идентификатор пользователя
    telegram_id BIGINT UNIQUE NOT NULL, -- Telegram ID пользователя
    username VARCHAR(255),       -- Имя пользователя в Telegram
    first_name VARCHAR(255),     -- Имя
    last_name VARCHAR(255)       -- Фамилия
);

-- Таблица слов
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,       -- Уникальный идентификатор слова
    target_word VARCHAR(255) NOT NULL,   -- Слово на английском
    translate_word VARCHAR(255) NOT NULL, -- Перевод слова на русском
    user_id BIGINT DEFAULT NULL   -- Идентификатор пользователя, если слово добавлено пользователем
);

-- Вставка начальных данных
INSERT INTO words (target_word, translate_word) VALUES
('Red', 'Красный'),
('Blue', 'Синий'),
('Green', 'Зелёный'),
('Yellow', 'Жёлтый'),
('I', 'Я'),
('You', 'Ты'),
('He', 'Он'),
('She', 'Она'),
('We', 'Мы'),
('They', 'Они');
