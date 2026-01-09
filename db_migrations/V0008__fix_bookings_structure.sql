-- Добавляем недостающие поля в таблицу bookings
ALTER TABLE t_p5914469_beauty_salon_project.bookings 
ADD COLUMN IF NOT EXISTS master_id INTEGER REFERENCES t_p5914469_beauty_salon_project.masters(id),
ADD COLUMN IF NOT EXISTS service_id INTEGER REFERENCES t_p5914469_beauty_salon_project.services(id),
ADD COLUMN IF NOT EXISTS client_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS client_phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS booking_date DATE,
ADD COLUMN IF NOT EXISTS booking_time TIME,
ADD COLUMN IF NOT EXISTS duration INTEGER,
ADD COLUMN IF NOT EXISTS price INTEGER,
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'confirmed';

-- Создаём индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_bookings_master_date ON t_p5914469_beauty_salon_project.bookings(master_id, booking_date);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON t_p5914469_beauty_salon_project.bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON t_p5914469_beauty_salon_project.bookings(booking_date);