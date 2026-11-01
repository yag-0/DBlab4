-- 1. Таблиця жанрів
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Таблиця кінематографістів (актори, режисери, оператори тощо)
CREATE TABLE persons (
    person_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Таблиця посад / ролей у знімальній групі
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- Наприклад: 'Режисер', 'Актор', 'Сценарист', 'Оператор'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Таблиця фільмів
CREATE TABLE movies (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    release_year INT CHECK (release_year BETWEEN 1888 AND 2100),
    duration_minutes INT CHECK (duration_minutes > 0),
    rating DECIMAL(3, 1) CHECK (rating >= 0.0 AND rating <= 10.0),
    budget DECIMAL(15, 2) CHECK (budget >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Проміжна таблиця: Фільми <-> Жанри (Багато-до-Багатьох)
CREATE TABLE movie_genres (
    movie_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE CASCADE
);

-- 6. Проміжна таблиця: Знімальна група (Фільми <-> Особи <-> Ролі)
CREATE TABLE movie_crew (
    movie_id INT NOT NULL,
    person_id INT NOT NULL,
    role_id INT NOT NULL,
    character_name VARCHAR(100), -- Заповнюється тільки якщо role = 'Актор'
    PRIMARY KEY (movie_id, person_id, role_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Створення індексів для покращення швидкодії пошуку та зв'язування
-- -----------------------------------------------------------------------------

-- Індекси для швидкого пошуку фільмів
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_release_year ON movies(release_year);
CREATE INDEX idx_movies_rating ON movies(rating);

-- Індекси для зовнішніх ключів зв'язків жанрів
CREATE INDEX idx_movie_genres_genre_id ON movie_genres(genre_id);

-- Індекси для швидкого вибору складу фільму або фільмографії людини
CREATE INDEX idx_movie_crew_person_id ON movie_crew(person_id);
CREATE INDEX idx_movie_crew_role_id ON movie_crew(role_id);