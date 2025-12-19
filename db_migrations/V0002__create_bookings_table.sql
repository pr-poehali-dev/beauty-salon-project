-- Создание таблицы для заявок
CREATE TABLE IF NOT EXISTS t_p5914469_beauty_salon_project.bookings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    service VARCHAR(255) NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);