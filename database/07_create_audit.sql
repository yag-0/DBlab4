-- =============================================================================
-- КРОК 12.2: МЕХАНІЗМ ЛОГУВАННЯ ОПЕРАЦІЙ (АУДИТ)
-- =============================================================================

CREATE TABLE activity_log (
    log_id SERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Функція для логування операцій
CREATE OR REPLACE FUNCTION log_activity(
    p_user_id INT,
    p_action VARCHAR,
    p_table_name VARCHAR,
    p_record_id INT,
    p_details TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO activity_log (user_id, action, table_name, record_id, details)
    VALUES (p_user_id, p_action, p_table_name, p_record_id, p_details);
END;
$$ LANGUAGE plpgsql;