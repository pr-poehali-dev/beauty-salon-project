-- Добавляем telegram_id для связи клиентов с их Telegram аккаунтами
ALTER TABLE t_p5914469_beauty_salon_project.bookings 
ADD COLUMN IF NOT EXISTS telegram_id BIGINT;

-- Создаём индекс для быстрого поиска по telegram_id
CREATE INDEX IF NOT EXISTS idx_bookings_telegram_id 
ON t_p5914469_beauty_salon_project.bookings(telegram_id);

-- Обновляем существующие записи из user_sessions если возможно
UPDATE t_p5914469_beauty_salon_project.bookings b
SET telegram_id = us.chat_id
FROM t_p5914469_beauty_salon_project.user_sessions us
WHERE b.phone = (us.session_data::jsonb->>'phone')
AND b.telegram_id IS NULL;