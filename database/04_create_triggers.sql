-- =============================================================================
-- КРОК 8: ТРИГЕРИ ТА АВТОМАТИЗАЦІЯ ДЛЯ КІНОБАЗИ
-- =============================================================================

-- 1. Таблиця для аудиту змін бюджетів фільмів
CREATE TABLE movie_budget_audit (
    audit_id SERIAL PRIMARY KEY,
    movie_id INT,
    operation VARCHAR(10),
    old_budget DECIMAL(15, 2),
    new_budget DECIMAL(15, 2),
    changed_by VARCHAR(50),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Тригер 1: Логування змін бюджету фільмів
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION log_movie_budget_change()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND (OLD.budget IS DISTINCT FROM NEW.budget) THEN
        INSERT INTO movie_budget_audit (movie_id, operation, old_budget, new_budget, changed_by)
        VALUES (NEW.movie_id, 'UPDATE', OLD.budget, NEW.budget, current_user);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER movie_budget_audit_trigger
AFTER UPDATE ON movies
FOR EACH ROW
EXECUTE FUNCTION log_movie_budget_change();


-- -----------------------------------------------------------------------------
-- Тригер 2: Автоматичне оновлення дати модифікації або фіксації часу
-- -----------------------------------------------------------------------------
-- Примітка: оскільки у нас використовується created_at, зробимо тригер 
-- для оновлення службового поля (або ж просто залишимо логіку оновлення часу зміни).
CREATE OR REPLACE FUNCTION update_movie_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- Можна додати поле updated_at, якщо воно є, або оновлювати created_at за потребою
    -- Для прикладу зберігаємо логіку шаблону:
    NEW.created_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Закоментовано, щоб не перезаписувати первинну дату створення автоматично, 
-- але залишено як приклад структури тригера:
-- CREATE TRIGGER movie_modified_timestamp
-- BEFORE UPDATE ON movies
-- FOR EACH ROW
-- EXECUTE FUNCTION update_movie_timestamp();


-- -----------------------------------------------------------------------------
-- Тригер 3: Валідація даних фільму перед вставкою або оновленням
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION validate_movie_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Перевірка року випуску (фільми почали з'являтися з кінця XIX століття і не можуть бути з далекого майбутнього)
    IF NEW.release_year < 1888 OR NEW.release_year > (EXTRACT(YEAR FROM CURRENT_DATE) + 5) THEN
        RAISE EXCEPTION 'Некоректний рік випуску фільму: %', NEW.release_year;
    END IF;

    -- Перевірка тривалості фільму (у хвилинах)
    IF NEW.duration_minutes IS NOT NULL AND (NEW.duration_minutes < 1 OR NEW.duration_minutes > 600) THEN
        RAISE EXCEPTION 'Некоректна тривалість фільму (має бути від 1 до 600 хвилин)';
    END IF;

    -- Перевірка бюджету (не може бути від'ємним)
    IF NEW.budget IS NOT NULL AND NEW.budget < 0 THEN
        RAISE EXCEPTION 'Бюджет фільму не може бути від''ємним';
    END IF;

    -- Перевірка рейтингу (від 0 до 10)
    IF NEW.rating IS NOT NULL AND (NEW.rating < 0.0 OR NEW.rating > 10.0) THEN
        RAISE EXCEPTION 'Рейтинг фільму має бути в межах від 0.0 до 10.0';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_movie_before_insert_update
BEFORE INSERT OR UPDATE ON movies
FOR EACH ROW
EXECUTE FUNCTION validate_movie_data();