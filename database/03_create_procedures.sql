-- =============================================================================
-- КРОК 7: ЗБЕРЕЖЕНІ ФУНКЦІЇ ТА ПРОЦЕДУРИ ДЛЯ КІНОБАЗИ
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Процедура 1: Додавання фільму з автоматичним створенням режисера (якщо його немає в базі)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION add_movie_with_director(
    p_title VARCHAR,
    p_year INT,
    p_duration INT,
    p_rating DECIMAL,
    p_budget DECIMAL,
    p_dir_first VARCHAR,
    p_dir_last VARCHAR
) RETURNS INT AS $$
DECLARE
    v_person_id INT;
    v_movie_id INT;
    v_role_id INT;
BEGIN
    -- 1. Перевірка існування режисера в таблиці persons
    SELECT person_id INTO v_person_id
    FROM persons
    WHERE first_name = p_dir_first AND last_name = p_dir_last;

    -- 2. Створення режисера, якщо він ще не існує
    IF v_person_id IS NULL THEN
        INSERT INTO persons (first_name, last_name, country)
        VALUES (p_dir_first, p_dir_last, 'Не вказано')
        RETURNING person_id INTO v_person_id;
    END IF;

    -- 3. Отримання ID ролі 'Режисер' із довідника roles
    SELECT role_id INTO v_role_id
    FROM roles
    WHERE name = 'Режисер';

    -- Якщо роль 'Режисер' відсутня в довіднику, створюємо її автоматично
    IF v_role_id IS NULL THEN
        INSERT INTO roles (name)
        VALUES ('Режисер')
        RETURNING role_id INTO v_role_id;
    END IF;

    -- 4. Створення самого фільму
    INSERT INTO movies (title, release_year, duration_minutes, rating, budget)
    VALUES (p_title, p_year, p_duration, p_rating, p_budget)
    RETURNING movie_id INTO v_movie_id;

    -- 5. Додавання запису у знімальну групу (movie_crew) про те, що ця особа є режисером фільму
    INSERT INTO movie_crew (movie_id, person_id, role_id, character_name)
    VALUES (v_movie_id, v_person_id, v_role_id, NULL);

    RETURN v_movie_id;
END;
$$ LANGUAGE plpgsql;


-- -----------------------------------------------------------------------------
-- Процедура 2: Коригування бюджету фільмів конкретного кінематографіста на заданий відсоток
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_person_movies_budget(
    p_person_id INT,
    p_percent_change DECIMAL
) RETURNS TABLE(movie_id INT, old_budget DECIMAL, new_budget DECIMAL) AS $$
BEGIN
    RETURN QUERY
    UPDATE movies m
    SET budget = m.budget * (1 + p_percent_change / 100)
    FROM movie_crew mc
    WHERE m.movie_id = mc.movie_id 
      AND mc.person_id = p_person_id
      AND m.budget IS NOT NULL
    RETURNING m.movie_id,
              (m.budget / (1 + p_percent_change / 100)) AS old_budget,
              m.budget AS new_budget;
END;
$$ LANGUAGE plpgsql;


-- -----------------------------------------------------------------------------
-- Процедура 3: Отримання розширеної статистики по фільмографії конкретного кінематографіста
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_person_movie_statistics(p_person_id INT)
RETURNS TABLE(
    total_movies INT,
    avg_budget DECIMAL,
    min_budget DECIMAL,
    max_budget DECIMAL,
    total_duration INT,
    earliest_year INT,
    latest_year INT,
    avg_rating DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(m.movie_id)::INT AS total_movies,
        ROUND(AVG(m.budget), 2)::DECIMAL(15,2) AS avg_budget,
        MIN(m.budget)::DECIMAL(15,2) AS min_budget,
        MAX(m.budget)::DECIMAL(15,2) AS max_budget,
        SUM(m.duration_minutes)::INT AS total_duration,
        MIN(m.release_year)::INT AS earliest_year,
        MAX(m.release_year)::INT AS latest_year,
        ROUND(AVG(m.rating), 1)::DECIMAL(3,1) AS avg_rating
    FROM movies m
    INNER JOIN movie_crew mc ON m.movie_id = mc.movie_id
    WHERE mc.person_id = p_person_id;
END;
$$ LANGUAGE plpgsql;