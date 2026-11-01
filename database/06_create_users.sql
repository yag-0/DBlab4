-- =============================================================================
-- КРОК 12.1: СТВОРЕННЯ ТАБЛИЦІ КОРИСТУВАЧІВ ТА АВТОРИЗАЦІЇ
-- =============================================================================

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Додавання адміністратора за замовчуванням
-- Пароль: admin123 (у реальному проєкті використовуйте безпечне хешування)
INSERT INTO users (username, password_hash, email, role) VALUES
('admin', 'admin123', 'admin@cinemadb.com', 'admin');