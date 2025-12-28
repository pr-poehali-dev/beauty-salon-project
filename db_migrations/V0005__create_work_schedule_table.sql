-- Создание таблицы для графика работы мастеров
CREATE TABLE IF NOT EXISTS work_schedule (
    id SERIAL PRIMARY KEY,
    master VARCHAR(100) NOT NULL,
    work_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(master, work_date, start_time)
);