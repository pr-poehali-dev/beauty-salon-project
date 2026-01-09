-- Таблица для хранения сессий пользователей (данные клиента во время записи)
CREATE TABLE IF NOT EXISTS t_p5914469_beauty_salon_project.user_sessions (
    chat_id BIGINT PRIMARY KEY,
    session_data JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица для блокировок времени мастерами
CREATE TABLE IF NOT EXISTS t_p5914469_beauty_salon_project.master_blocks (
    id SERIAL PRIMARY KEY,
    master_id INTEGER NOT NULL REFERENCES t_p5914469_beauty_salon_project.masters(id),
    block_date DATE NOT NULL,
    block_start TIME NOT NULL,
    block_end TIME NOT NULL,
    reason VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_master_blocks_date ON t_p5914469_beauty_salon_project.master_blocks(master_id, block_date);
