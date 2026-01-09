import json
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor


TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_API = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'

# ID мастеров для доступа к админ-панели
MASTER_IDS = [123456789, 987654321]  # Замените на реальные Telegram ID мастеров


def handler(event: dict, context) -> dict:
    """Telegram бот онлайн-записи с кнопочным интерфейсом"""
    
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            update = body
            print(f"[DEBUG] Received update: {json.dumps(update)}")
            
            if 'message' in update:
                return handle_message(update['message'])
            elif 'callback_query' in update:
                callback_data = update['callback_query'].get('data', 'NO DATA')
                print(f"[DEBUG] Processing callback: {callback_data}")
                return handle_callback(update['callback_query'])
            
            return response(200, {'ok': True})
            
        except Exception as e:
            return response(500, {'error': str(e)})
    
    return response(405, {'error': 'Method not allowed'})


def handle_message(message: dict) -> dict:
    """Обработка текстовых сообщений (имя, телефон, сообщение мастеру)"""
    chat_id = message['chat']['id']
    text = message.get('text', '')
    
    if text == '/start':
        return send_role_selection(chat_id)
    
    # Проверяем, ждём ли мы ввод данных от клиента
    session = get_user_session(chat_id)
    
    if session and session.get('state') == 'waiting_name':
        return handle_client_name(chat_id, text, session)
    elif session and session.get('state') == 'waiting_phone':
        return handle_client_phone(chat_id, text, session)
    elif session and session.get('state') == 'waiting_message':
        return handle_client_message(chat_id, text, session)
    
    return response(200, {'ok': True})


def handle_callback(callback: dict) -> dict:
    """Обработка нажатий на кнопки"""
    chat_id = callback['message']['chat']['id']
    message_id = callback['message']['message_id']
    data = callback['data']
    callback_id = callback['id']
    user_id = callback['from']['id']
    
    answer_callback(callback_id)
    
    if data == 'role_client':
        return start_client_flow(chat_id, message_id)
    elif data == 'role_master':
        return start_master_flow(chat_id, message_id, user_id)
    
    # Клиентские действия
    elif data.startswith('master_'):
        master_id = int(data.split('_')[1])
        return send_services_list(chat_id, message_id, master_id)
    elif data.startswith('service_'):
        service_id = int(data.split('_')[1])
        return send_date_selection(chat_id, message_id, service_id)
    elif data.startswith('date_'):
        parts = data.split('_')
        service_id = int(parts[1])
        date = parts[2]
        print(f"[DEBUG] Date selected: service_id={service_id}, date={date}")
        return send_time_selection(chat_id, message_id, service_id, date)
    elif data.startswith('time_'):
        parts = data.split('_')
        service_id = int(parts[1])
        date = parts[2]
        time = parts[3]
        return request_client_name(chat_id, message_id, service_id, date, time)
    elif data.startswith('confirm_'):
        booking_id = data.split('_')[1]
        return confirm_booking_final(chat_id, message_id, booking_id)
    elif data.startswith('cancel_booking_'):
        booking_id = data.split('_')[2]
        return cancel_booking_by_client(chat_id, message_id, booking_id)
    
    # Мастерские действия
    elif data == 'master_bookings':
        return show_master_bookings(chat_id, message_id, user_id)
    elif data == 'master_add_booking':
        return master_add_booking_flow(chat_id, message_id)
    elif data == 'master_cancel_booking':
        return master_cancel_booking_flow(chat_id, message_id, user_id)
    elif data == 'master_block_time':
        return master_block_time_flow(chat_id, message_id)
    elif data == 'back_to_master_menu':
        return send_master_menu(chat_id, message_id)
    elif data.startswith('cancel_booking_master_'):
        booking_id = data.split('_')[3]
        return cancel_booking_by_master(chat_id, message_id, booking_id)
    
    elif data == 'skip_message':
        session = get_user_session(chat_id)
        if session:
            return show_booking_confirmation(chat_id, message_id, session)
    
    elif data == 'noop':
        return response(200, {'ok': True})
    
    return response(200, {'ok': True})


# ==================== ВЫБОР РОЛИ ====================

def send_role_selection(chat_id: int) -> dict:
    """Выбор роли: Клиент или Мастер"""
    text = """👋 Добро пожаловать в студию красоты!

Выберите вашу роль:"""
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '🧍 Клиент', 'callback_data': 'role_client'}],
            [{'text': '👩‍💼 Мастер', 'callback_data': 'role_master'}]
        ]
    }
    
    send_message(chat_id, text, keyboard)
    return response(200, {'ok': True})


# ==================== ПОТОК КЛИЕНТА ====================

def start_client_flow(chat_id: int, message_id: int) -> dict:
    """Начало потока записи для клиента"""
    return send_masters_list(chat_id, message_id)


def send_masters_list(chat_id: int, message_id: int) -> dict:
    """Список мастеров"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT id, name FROM t_p5914469_beauty_salon_project.masters ORDER BY id")
    masters = cur.fetchall()
    
    cur.close()
    conn.close()
    
    keyboard = {
        'inline_keyboard': [
            [{'text': master['name'], 'callback_data': f"master_{master['id']}"}]
            for master in masters
        ]
    }
    
    edit_message(chat_id, message_id, "Выберите мастера:", keyboard)
    return response(200, {'ok': True})


def send_services_list(chat_id: int, message_id: int, master_id: int) -> dict:
    """Список услуг мастера с ценой и длительностью"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT name FROM t_p5914469_beauty_salon_project.masters WHERE id = %s", (master_id,))
    master = cur.fetchone()
    master_name = master['name']
    
    cur.execute("""
        SELECT id, category, name, price, duration 
        FROM t_p5914469_beauty_salon_project.services 
        WHERE master_id = %s 
        ORDER BY category, name
    """, (master_id,))
    services = cur.fetchall()
    
    cur.close()
    conn.close()
    
    keyboard = {'inline_keyboard': []}
    current_category = None
    
    for service in services:
        if service['category'] != current_category:
            current_category = service['category']
            keyboard['inline_keyboard'].append([{'text': f"📌 {current_category}", 'callback_data': 'noop'}])
        
        hours = service['duration'] // 60
        minutes = service['duration'] % 60
        time_str = f"{hours}ч {minutes}м" if hours > 0 else f"{minutes}м"
        
        text = f"{service['name']} | {service['price']} | {time_str}"
        keyboard['inline_keyboard'].append([{'text': text, 'callback_data': f"service_{service['id']}"}])
    
    edit_message(chat_id, message_id, f"Услуги мастера {master_name}:\n\nВыберите услугу:", keyboard)
    return response(200, {'ok': True})


def send_date_selection(chat_id: int, message_id: int, service_id: int) -> dict:
    """Календарь для выбора даты"""
    keyboard = {'inline_keyboard': []}
    
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    
    today = datetime.now()
    for i in range(14):
        date = today + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        weekday = weekdays[date.weekday()]
        display = date.strftime(f'%d.%m ({weekday})')
        keyboard['inline_keyboard'].append([{'text': display, 'callback_data': f"date_{service_id}_{date_str}"}])
    
    edit_message(chat_id, message_id, "Выберите дату:", keyboard)
    return response(200, {'ok': True})


def send_time_selection(chat_id: int, message_id: int, service_id: int, date: str) -> dict:
    """Доступное время с учётом длительности процедур и блокировок"""
    print(f"[DEBUG] send_time_selection called: service_id={service_id}, date={date}")
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT master_id, duration FROM t_p5914469_beauty_salon_project.services WHERE id = %s", (service_id,))
    service = cur.fetchone()
    master_id = service['master_id']
    service_duration = service['duration']
    
    # Получаем все записи на эту дату
    cur.execute("""
        SELECT booking_time, duration 
        FROM t_p5914469_beauty_salon_project.bookings 
        WHERE master_id = %s AND booking_date = %s AND status != 'cancelled'
        ORDER BY booking_time
    """, (master_id, date))
    bookings = cur.fetchall()
    
    # Получаем блокировки времени
    cur.execute("""
        SELECT block_start, block_end
        FROM t_p5914469_beauty_salon_project.master_blocks
        WHERE master_id = %s AND block_date = %s
        ORDER BY block_start
    """, (master_id, date))
    blocks = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Собираем все занятые слоты
    occupied_slots = []
    
    for booking in bookings:
        start = datetime.strptime(str(booking['booking_time']), '%H:%M:%S')
        duration = booking['duration']
        end = start + timedelta(minutes=duration)
        occupied_slots.append((start, end))
    
    for block in blocks:
        start = datetime.strptime(str(block['block_start']), '%H:%M:%S')
        end = datetime.strptime(str(block['block_end']), '%H:%M:%S')
        occupied_slots.append((start, end))
    
    def is_time_available(start_time: datetime, duration: int) -> bool:
        end_time = start_time + timedelta(minutes=duration)
        for occ_start, occ_end in occupied_slots:
            if not (end_time <= occ_start or start_time >= occ_end):
                return False
        return True
    
    keyboard = {'inline_keyboard': []}
    work_start = datetime.strptime(f"{date} 09:00", '%Y-%m-%d %H:%M')
    work_end = datetime.strptime(f"{date} 20:00", '%Y-%m-%d %H:%M')
    
    current = work_start
    row = []
    while current < work_end:
        if is_time_available(current, service_duration):
            time_str = current.strftime('%H:%M')
            row.append({'text': time_str, 'callback_data': f"time_{service_id}_{date}_{time_str}"})
            if len(row) == 3:
                keyboard['inline_keyboard'].append(row)
                row = []
        current += timedelta(minutes=30)
    
    if row:
        keyboard['inline_keyboard'].append(row)
    
    if not keyboard['inline_keyboard']:
        edit_message(chat_id, message_id, f"❌ К сожалению, на {date} нет свободного времени")
    else:
        edit_message(chat_id, message_id, f"Выберите время на {date}:", keyboard)
    
    return response(200, {'ok': True})


def request_client_name(chat_id: int, message_id: int, service_id: int, date: str, time: str) -> dict:
    """Запрос имени клиента"""
    # Сохраняем данные в сессию
    save_user_session(chat_id, {
        'state': 'waiting_name',
        'service_id': service_id,
        'date': date,
        'time': time
    })
    
    edit_message(chat_id, message_id, "Введите ваше имя:")
    return response(200, {'ok': True})


def handle_client_name(chat_id: int, name: str, session: dict) -> dict:
    """Обработка имени клиента"""
    session['client_name'] = name
    session['state'] = 'waiting_phone'
    save_user_session(chat_id, session)
    
    send_message(chat_id, "Введите ваш номер телефона:")
    return response(200, {'ok': True})


def handle_client_phone(chat_id: int, phone: str, session: dict) -> dict:
    """Обработка телефона клиента"""
    session['client_phone'] = phone
    session['state'] = 'waiting_message'
    save_user_session(chat_id, session)
    
    keyboard = {
        'inline_keyboard': [
            [{'text': 'Пропустить', 'callback_data': 'skip_message'}]
        ]
    }
    
    send_message(chat_id, "Введите сообщение мастеру (или нажмите 'Пропустить'):", keyboard)
    return response(200, {'ok': True})


def handle_client_message(chat_id: int, message: str, session: dict) -> dict:
    """Обработка сообщения мастеру"""
    session['client_message'] = message
    save_user_session(chat_id, session)
    
    return show_booking_confirmation(chat_id, None, session)


def show_booking_confirmation(chat_id: int, message_id: int or None, session: dict) -> dict:
    """Показ карточки подтверждения записи"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT s.name, s.price, s.duration, s.master_id, m.name as master_name
        FROM t_p5914469_beauty_salon_project.services s
        JOIN t_p5914469_beauty_salon_project.masters m ON s.master_id = m.id
        WHERE s.id = %s
    """, (session['service_id'],))
    service = cur.fetchone()
    
    cur.close()
    conn.close()
    
    hours = service['duration'] // 60
    minutes = service['duration'] % 60
    time_str = f"{hours}ч {minutes}м" if hours > 0 else f"{minutes}м"
    
    text = f"""📋 Подтверждение записи:

👩‍💼 Мастер: {service['master_name']}
✨ Услуга: {service['name']}
💰 Цена: {service['price']}
📅 Дата: {session['date']}
🕐 Время: {session['time']}
⏱ Длительность: {time_str}

👤 Имя: {session['client_name']}
📞 Телефон: {session['client_phone']}"""
    
    if session.get('client_message'):
        text += f"\n💬 Сообщение: {session['client_message']}"
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '✅ Подтвердить', 'callback_data': f"confirm_temp"}],
            [{'text': '❌ Отменить', 'callback_data': 'role_client'}]
        ]
    }
    
    if message_id:
        edit_message(chat_id, message_id, text, keyboard)
    else:
        send_message(chat_id, text, keyboard)
    
    return response(200, {'ok': True})


def confirm_booking_final(chat_id: int, message_id: int, booking_id: str) -> dict:
    """Финальное подтверждение и сохранение записи"""
    session = get_user_session(chat_id)
    
    if not session:
        send_message(chat_id, "❌ Ошибка: данные сессии не найдены")
        return response(200, {'ok': True})
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT master_id, duration FROM t_p5914469_beauty_salon_project.services WHERE id = %s", (session['service_id'],))
    service = cur.fetchone()
    
    cur.execute("""
        INSERT INTO t_p5914469_beauty_salon_project.bookings 
        (master_id, service_id, booking_date, booking_time, duration, client_name, client_phone, client_message, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'confirmed')
        RETURNING id
    """, (
        service['master_id'],
        session['service_id'],
        session['date'],
        session['time'],
        service['duration'],
        session['client_name'],
        session['client_phone'],
        session.get('client_message', '')
    ))
    
    booking = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    # Очищаем сессию
    clear_user_session(chat_id)
    
    text = f"""✅ Запись успешно создана!

Мы ждём вас {session['date']} в {session['time']}

До встречи! 💫"""
    
    edit_message(chat_id, message_id, text)
    return response(200, {'ok': True})


# ==================== ПОТОК МАСТЕРА ====================

def start_master_flow(chat_id: int, message_id: int, user_id: int) -> dict:
    """Начало потока для мастера"""
    # Проверка доступа (можно по Telegram ID)
    # if user_id not in MASTER_IDS:
    #     edit_message(chat_id, message_id, "❌ У вас нет доступа к панели мастера")
    #     return response(200, {'ok': True})
    
    return send_master_menu(chat_id, message_id)


def send_master_menu(chat_id: int, message_id: int) -> dict:
    """Главное меню мастера"""
    text = """👩‍💼 Панель мастера

Выберите действие:"""
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '📋 Все записи', 'callback_data': 'master_bookings'}],
            [{'text': '➕ Добавить запись', 'callback_data': 'master_add_booking'}],
            [{'text': '❌ Отменить запись', 'callback_data': 'master_cancel_booking'}],
            [{'text': '🚫 Заблокировать время', 'callback_data': 'master_block_time'}]
        ]
    }
    
    edit_message(chat_id, message_id, text, keyboard)
    return response(200, {'ok': True})


def show_master_bookings(chat_id: int, message_id: int, user_id: int) -> dict:
    """Показать все записи мастера"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT b.id, b.booking_date, b.booking_time, b.duration, b.client_name, b.client_phone, 
               b.client_message, s.name as service_name, m.name as master_name
        FROM t_p5914469_beauty_salon_project.bookings b
        JOIN t_p5914469_beauty_salon_project.services s ON b.service_id = s.id
        JOIN t_p5914469_beauty_salon_project.masters m ON b.master_id = m.id
        WHERE b.status = 'confirmed' AND b.booking_date >= CURRENT_DATE
        ORDER BY b.booking_date, b.booking_time
        LIMIT 20
    """)
    bookings = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if not bookings:
        text = "📋 Нет записей на ближайшее время"
    else:
        text = "📋 Записи:\n\n"
        for b in bookings:
            hours = b['duration'] // 60
            minutes = b['duration'] % 60
            time_str = f"{hours}ч {minutes}м" if hours > 0 else f"{minutes}м"
            
            text += f"• {b['booking_date']} в {b['booking_time']}\n"
            text += f"  {b['master_name']} — {b['service_name']}\n"
            text += f"  Клиент: {b['client_name']}, {b['client_phone']}\n"
            text += f"  Длительность: {time_str}\n"
            if b['client_message']:
                text += f"  Сообщение: {b['client_message']}\n"
            text += "\n"
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '◀️ Назад', 'callback_data': 'back_to_master_menu'}]
        ]
    }
    
    edit_message(chat_id, message_id, text, keyboard)
    return response(200, {'ok': True})


def master_add_booking_flow(chat_id: int, message_id: int) -> dict:
    """Добавление записи мастером (упрощённый вариант - через выбор мастера)"""
    text = "➕ Для добавления записи выберите мастера:"
    return send_masters_list(chat_id, message_id)


def master_cancel_booking_flow(chat_id: int, message_id: int, user_id: int) -> dict:
    """Отмена записи мастером"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT b.id, b.booking_date, b.booking_time, s.name as service_name, b.client_name
        FROM t_p5914469_beauty_salon_project.bookings b
        JOIN t_p5914469_beauty_salon_project.services s ON b.service_id = s.id
        WHERE b.status = 'confirmed' AND b.booking_date >= CURRENT_DATE
        ORDER BY b.booking_date, b.booking_time
        LIMIT 10
    """)
    bookings = cur.fetchall()
    
    cur.close()
    conn.close()
    
    if not bookings:
        keyboard = {
            'inline_keyboard': [
                [{'text': '◀️ Назад', 'callback_data': 'back_to_master_menu'}]
            ]
        }
        edit_message(chat_id, message_id, "Нет записей для отмены", keyboard)
        return response(200, {'ok': True})
    
    keyboard = {'inline_keyboard': []}
    for b in bookings:
        text = f"{b['booking_date']} {b['booking_time']} — {b['client_name']}"
        keyboard['inline_keyboard'].append([{'text': text, 'callback_data': f"cancel_booking_master_{b['id']}"}])
    
    keyboard['inline_keyboard'].append([{'text': '◀️ Назад', 'callback_data': 'back_to_master_menu'}])
    
    edit_message(chat_id, message_id, "Выберите запись для отмены:", keyboard)
    return response(200, {'ok': True})


def cancel_booking_by_master(chat_id: int, message_id: int, booking_id: str) -> dict:
    """Отмена записи мастером"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE t_p5914469_beauty_salon_project.bookings 
        SET status = 'cancelled'
        WHERE id = %s
    """, (booking_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    edit_message(chat_id, message_id, "✅ Запись отменена")
    return response(200, {'ok': True})


def master_block_time_flow(chat_id: int, message_id: int) -> dict:
    """Блокировка времени (упрощённая версия)"""
    text = """🚫 Блокировка времени

Функция в разработке. Для блокировки времени обратитесь к администратору."""
    
    keyboard = {
        'inline_keyboard': [
            [{'text': '◀️ Назад', 'callback_data': 'back_to_master_menu'}]
        ]
    }
    
    edit_message(chat_id, message_id, text, keyboard)
    return response(200, {'ok': True})


# ==================== СЕССИИ ПОЛЬЗОВАТЕЛЕЙ ====================

def get_user_session(chat_id: int) -> dict or None:
    """Получить сессию пользователя"""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT session_data 
            FROM t_p5914469_beauty_salon_project.user_sessions 
            WHERE chat_id = %s
        """, (chat_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return json.loads(result['session_data'])
        return None
    except:
        return None


def save_user_session(chat_id: int, session_data: dict) -> None:
    """Сохранить сессию пользователя"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO t_p5914469_beauty_salon_project.user_sessions (chat_id, session_data, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (chat_id) 
            DO UPDATE SET session_data = %s, updated_at = NOW()
        """, (chat_id, json.dumps(session_data), json.dumps(session_data)))
        
        conn.commit()
        cur.close()
        conn.close()
    except:
        pass


def clear_user_session(chat_id: int) -> None:
    """Очистить сессию пользователя"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM t_p5914469_beauty_salon_project.user_sessions WHERE chat_id = %s", (chat_id,))
        
        conn.commit()
        cur.close()
        conn.close()
    except:
        pass


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_db():
    """Подключение к БД"""
    return psycopg2.connect(os.environ['DATABASE_URL'])


def response(status: int, body: dict = None) -> dict:
    """HTTP ответ"""
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body or {}),
        'isBase64Encoded': False
    }


def send_message(chat_id: int, text: str, keyboard: dict = None) -> None:
    """Отправка сообщения"""
    import urllib.request
    
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    if keyboard:
        data['reply_markup'] = keyboard
    
    req = urllib.request.Request(
        f'{TELEGRAM_API}/sendMessage',
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        urllib.request.urlopen(req)
    except:
        pass


def edit_message(chat_id: int, message_id: int, text: str, keyboard: dict = None) -> None:
    """Редактирование сообщения"""
    import urllib.request
    
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    if keyboard:
        data['reply_markup'] = keyboard
    
    req = urllib.request.Request(
        f'{TELEGRAM_API}/editMessageText',
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        urllib.request.urlopen(req)
    except:
        pass


def answer_callback(callback_id: str) -> None:
    """Ответ на callback query"""
    import urllib.request
    
    data = {'callback_query_id': callback_id}
    
    req = urllib.request.Request(
        f'{TELEGRAM_API}/answerCallbackQuery',
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        urllib.request.urlopen(req)
    except:
        pass