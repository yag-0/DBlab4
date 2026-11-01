-- =============================================================================
-- КРОК 9: СТВОРЕННЯ ПРЕДСТАВЛЕНЬ (VIEWS) ДЛЯ КІНОБАЗИ
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Представлення 1: Фільми з інформацією про їхніх режисерів
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW movies_with_directors AS
SELECT
    m.movie_id,
    m.title,
    m.release_year,
    m.duration_minutes,
    m.rating,
    m.budget,
    p.person_id AS director_id,
    p.first_name || ' ' || p.last_name AS director_name,
    p.country AS director_country,
    p.birth_date AS director_birth_date
FROM movies m
INNER JOIN movie_crew mc ON m.movie_id = mc.movie_id
INNER JOIN roles r ON mc.role_id = r.role_id
INNER JOIN persons p ON mc.person_id = p.person_id
WHERE r.name = 'Режисер';


-- -----------------------------------------------------------------------------
-- Представлення 2: Статистика по кінематографістах (кількість фільмів, бюджети, рейтинг)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW person_statistics AS
SELECT
    p.person_id,
    p.first_name || ' ' || p.last_name AS person_name,
    p.country,
    COUNT(m.movie_id) AS total_movies,
    ROUND(AVG(m.budget), 2)::DECIMAL(15,2) AS avg_movie_budget,
    SUM(m.duration_minutes) AS total_duration_minutes,
    MIN(m.release_year) AS earliest_movie_year,
    MAX(m.release_year) AS latest_movie_year,
    ROUND(AVG(m.rating), 1)::DECIMAL(3,1) AS avg_rating
FROM persons p
LEFT JOIN movie_crew mc ON p.person_id = mc.person_id
LEFT JOIN movies m ON mc.movie_id = m.movie_id
GROUP BY p.person_id, p.first_name, p.last_name, p.country;


-- -----------------------------------------------------------------------------
-- Представлення 3: Найдорожчий фільм кожного режисера
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW most_expensive_movies_by_director AS
SELECT DISTINCT ON (p.person_id)
    p.person_id,
    p.first_name || ' ' || p.last_name AS director_name,
    m.title AS most_expensive_movie,
    m.budget AS highest_budget,
    m.release_year
FROM persons p
INNER JOIN movie_crew mc ON p.person_id = mc.person_id
INNER JOIN roles r ON mc.role_id = r.role_id
INNER JOIN movies m ON mc.movie_id = m.movie_id
WHERE r.name = 'Режисер' AND m.budget IS NOT NULL
ORDER BY p.person_id, m.budget DESC;