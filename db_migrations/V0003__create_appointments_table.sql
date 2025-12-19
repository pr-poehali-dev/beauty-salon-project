-- Создание таблицы для записей по времени
CREATE TABLE IF NOT EXISTS t_p5914469_beauty_salon_project.appointments (
    id SERIAL PRIMARY KEY,
    master VARCHAR(50) NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    client_phone VARCHAR(50) NOT NULL,
    service VARCHAR(255) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    message TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(master, appointment_date, appointment_time)
);