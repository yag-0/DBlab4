-- =============================================================================
-- КРОК 6: КОЛЕКЦІЯ SQL-ЗАПИТІВ ДЛЯ КІНОБАЗИ
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Прості запити на вибірку даних з однієї таблиці з фільтрацією та сортуванням
-- Запит 1: Фільми, випущені з 2010 року включно, відсортовані за рейтингом (від найвищого)
-- -----------------------------------------------------------------------------
SELECT title, release_year, rating, budget
FROM movies
WHERE release_year >= 2010
ORDER BY rating DESC;


-- -----------------------------------------------------------------------------
-- 2. Запити з об'єднанням таблиць для отримання пов'язаних даних
-- Запит 2: Фільми разом із їхніми жанрами (об'єднання movies, movie_genres та genres)
-- -----------------------------------------------------------------------------
SELECT 
    m.title AS movie_title,
    m.release_year,
    g.name AS genre_name
FROM movies m
INNER JOIN movie_genres mg ON m.movie_id = mg.movie_id
INNER JOIN genres g ON mg.genre_id = g.genre_id
ORDER BY m.title;


-- -----------------------------------------------------------------------------
-- 3. Агрегатні запити для обчислення статистики
-- Запит 3: Статистика по кінематографістах (скільки фільмів людина створювала/знімалась, середній бюджет цих фільмів)
-- -----------------------------------------------------------------------------
SELECT 
    p.first_name || ' ' || p.last_name AS person_name,
    COUNT(mc.movie_id) AS movies_participated,
    ROUND(AVG(m.budget), 2) AS avg_movie_budget
FROM persons p
INNER JOIN movie_crew mc ON p.person_id = mc.person_id
INNER JOIN movies m ON mc.movie_id = m.movie_id
GROUP BY p.person_id, p.first_name, p.last_name
HAVING COUNT(mc.movie_id) > 0
ORDER BY movies_participated DESC;


-- -----------------------------------------------------------------------------
-- 4. Підзапити для складних умов вибірки
-- Запит 4: Фільми, чий бюджет вищий за середній бюджет усіх фільмів у базі
-- -----------------------------------------------------------------------------
SELECT title, release_year, budget
FROM movies
WHERE budget > (SELECT AVG(budget) FROM movies)
ORDER BY budget DESC;


-- -----------------------------------------------------------------------------
-- 5. Складні запити з кількома JOIN (повна інформація про знімальну групу фільму)
-- Запит 5: Детальна інформація: назва фільму, ім'я учасника знімальної групи, його роль (посада) та ім'я персонажа (якщо це актор)
-- -----------------------------------------------------------------------------
SELECT 
    m.title AS movie_title,
    m.release_year,
    p.first_name || ' ' || p.last_name AS crew_member,
    r.name AS role_type,
    COALESCE(mc.character_name, '—') AS character_name
FROM movies m
INNER JOIN movie_crew mc ON m.movie_id = mc.movie_id
INNER JOIN persons p ON mc.person_id = p.person_id
INNER JOIN roles r ON mc.role_id = r.role_id
ORDER BY m.title, r.name;