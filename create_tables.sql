CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    target_word VARCHAR(255) NOT NULL,
    translate_word VARCHAR(255) NOT NULL,
    user_id BIGINT DEFAULT NULL
);

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