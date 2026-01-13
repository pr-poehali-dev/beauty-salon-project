-- Переносим шугаринг от Алёны к Виктории
UPDATE t_p5914469_beauty_salon_project.services 
SET master_id = 1 
WHERE category = 'Шугаринг' AND master_id = 2;