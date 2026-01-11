import json
import os
from datetime import datetime, timedelta
from calendar import monthrange
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

MONTHS_RU = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
             'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
DAYS_RU = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

def response(status_code: int, body: dict) -> dict:
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(body, ensure_ascii=False),
        'isBase64Encoded': False
    }

def get_db():
    return psycopg2.connect(DATABASE_URL)

def send_message(chat_id: int, text: str, keyboard: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if keyboard:
        payload['reply_markup'] = keyboard
    resp = requests.post(url, json=payload)
    result = resp.json()
    print(f"[SEND] {resp.status_code} - {result}")
    return result

def edit_message(chat_id: int, message_id: int, text: str, keyboard: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'HTML'}
    if keyboard:
        payload['reply_markup'] = keyboard
    resp = requests.post(url, json=payload)
    result = resp.json()
    print(f"[EDIT] {resp.status_code} - {result}")
    return result

def answer_callback(callback_id: str, text: str = ""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    requests.post(url, json={'callback_query_id': callback_id, 'text': text})

def save_session(chat_id: int, data: dict):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO t_p5914469_beauty_salon_project.user_sessions (chat_id, session_data, updated_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (chat_id) DO UPDATE SET session_data = %s, updated_at = NOW()
    """, (chat_id, json.dumps(data), json.dumps(data)))
    conn.commit()
    cur.close()
    conn.close()

def get_session(chat_id: int) -> dict:
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT session_data FROM t_p5914469_beauty_salon_project.user_sessions WHERE chat_id = %s", (chat_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return json.loads(result['session_data']) if result and result['session_data'] else {}

def register_master_if_whitelisted(telegram_id: int, username: str) -> bool:
    """Автоматически регистрирует мастера по юзернейму"""
    MASTER_USERNAMES = {
        'kriwwwi': 'Виктория',
        'promisslab': 'Алёна',
        'sweetheart88': 'Алёна'  # Если это второй аккаунт Алёны
    }
    
    username_clean = username.lower().replace('@', '')
    
    if username_clean not in MASTER_USERNAMES:
        return False
    
    master_name = MASTER_USERNAMES[username_clean]
    
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE t_p5914469_beauty_salon_project.masters 
            SET telegram_chat_id = %s 
            WHERE name = %s AND (telegram_chat_id IS NULL OR telegram_chat_id = '')
        """, (str(telegram_id), master_name))
        conn.commit()
        updated = cur.rowcount > 0
        cur.close()
        conn.close()
        return updated
    except Exception as e:
        print(f"[ERROR] Failed to register master: {e}")
        return False

def get_user_info(telegram_id: int, username: str = '') -> dict:
    """Определяет тип пользователя: мастер или клиент"""
    print(f"[GET_USER_INFO] telegram_id={telegram_id}, username={username}")
    try:
        # Если есть username, пробуем автоматически зарегистрировать как мастера
        if username:
            registered = register_master_if_whitelisted(telegram_id, username)
            print(f"[GET_USER_INFO] Master registration attempt: {registered}")
        
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Проверяем, мастер ли это
        try:
            cur.execute("SELECT id, name FROM t_p5914469_beauty_salon_project.masters WHERE telegram_chat_id = %s", (str(telegram_id),))
            master = cur.fetchone()
            
            if master:
                cur.close()
                conn.close()
                return {'type': 'master', 'id': master['id'], 'name': master['name']}
        except Exception as e:
            print(f"[WARN] Master check failed: {e}")
        
        # Проверяем предыдущие записи клиента
        try:
            cur.execute("""
                SELECT client_name, client_phone 
                FROM t_p5914469_beauty_salon_project.bookings 
                WHERE telegram_id = %s AND client_name IS NOT NULL
                ORDER BY created_at DESC LIMIT 1
            """, (telegram_id,))
            client = cur.fetchone()
            
            if client:
                cur.close()
                conn.close()
                return {'type': 'client', 'name': client['client_name'], 'phone': client['client_phone']}
        except Exception as e:
            print(f"[WARN] Client check failed: {e}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] DB connection failed: {e}")
    
    return {'type': 'new_client'}

def build_calendar(year: int, month: int, service_id: int = None) -> dict:
    """Создаёт интерактивный календарь"""
    keyboard = {'inline_keyboard': []}
    
    # Заголовок с месяцем
    keyboard['inline_keyboard'].append([
        {'text': '◀️', 'callback_data': f'cal_prev_{year}_{month}_{service_id or 0}'},
        {'text': f'{MONTHS_RU[month-1]} {year}', 'callback_data': 'ignore'},
        {'text': '▶️', 'callback_data': f'cal_next_{year}_{month}_{service_id or 0}'}
    ])
    
    # Дни недели
    keyboard['inline_keyboard'].append([{'text': day, 'callback_data': 'ignore'} for day in DAYS_RU])
    
    # Первый день месяца и количество дней
    first_weekday = datetime(year, month, 1).weekday()  # 0=Пн, 6=Вс
    days_in_month = monthrange(year, month)[1]
    
    # Формируем недели
    week = []
    
    # Пустые ячейки до первого дня
    for _ in range(first_weekday):
        week.append({'text': ' ', 'callback_data': 'ignore'})
    
    # Дни месяца
    today = datetime.now().date()
    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day).date()
        
        # Проверяем, не прошедшая ли дата
        if date < today:
            week.append({'text': str(day), 'callback_data': 'ignore'})
        else:
            date_str = date.strftime('%Y-%m-%d')
            week.append({'text': str(day), 'callback_data': f'date_{service_id or 0}_{date_str}'})
        
        # Если неделя заполнена, добавляем в календарь
        if len(week) == 7:
            keyboard['inline_keyboard'].append(week)
            week = []
    
    # Добавляем последнюю неделю если есть
    if week:
        while len(week) < 7:
            week.append({'text': ' ', 'callback_data': 'ignore'})
        keyboard['inline_keyboard'].append(week)
    
    # Кнопка назад
    keyboard['inline_keyboard'].append([{'text': '« Назад', 'callback_data': 'back_to_services'}])
    
    return keyboard

def show_main_menu(chat_id: int, telegram_id: int, username: str = ''):
    """Главное меню в зависимости от типа пользователя"""
    print(f"[MENU] chat_id={chat_id}, telegram_id={telegram_id}, username={username}")
    user = get_user_info(telegram_id, username)
    print(f"[MENU] user type: {user['type']}")
    
    if user['type'] == 'master':
        text = f"👨‍💼 <b>Добро пожаловать, {user['name']}!</b>\n\nВы вошли как мастер."
        keyboard = {
            'inline_keyboard': [
                [{'text': '📅 Мои записи сегодня', 'callback_data': 'master_today'}],
                [{'text': '📋 Все записи', 'callback_data': 'master_all'}],
                [{'text': '🚫 Заблокировать время', 'callback_data': 'master_block'}]
            ]
        }
    elif user['type'] == 'client':
        text = f"👋 <b>С возвращением, {user['name']}!</b>\n\nХотите записаться снова?"
        keyboard = {
            'inline_keyboard': [
                [{'text': '📝 Записаться на процедуру', 'callback_data': 'client_book'}],
                [{'text': '📋 Мои записи', 'callback_data': 'client_bookings'}]
            ]
        }
    else:
        text = "👋 <b>Добро пожаловать в салон красоты!</b>\n\nЗапишитесь на процедуру прямо сейчас."
        keyboard = {
            'inline_keyboard': [
                [{'text': '📝 Записаться', 'callback_data': 'client_book'}]
            ]
        }
    
    send_message(chat_id, text, keyboard)

def show_masters(chat_id: int, message_id: int = None):
    """Список мастеров"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM t_p5914469_beauty_salon_project.masters ORDER BY name")
    masters = cur.fetchall()
    cur.close()
    conn.close()
    
    keyboard = {'inline_keyboard': []}
    for master in masters:
        keyboard['inline_keyboard'].append([{'text': f"👤 {master['name']}", 'callback_data': f"master_{master['id']}"}])
    
    keyboard['inline_keyboard'].append([{'text': '« Назад', 'callback_data': 'start'}])
    
    text = "👨‍💼 <b>Выберите мастера:</b>"
    
    if message_id:
        edit_message(chat_id, message_id, text, keyboard)
    else:
        send_message(chat_id, text, keyboard)

def show_services(chat_id: int, message_id: int, master_id: int):
    """Услуги мастера"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id, name, duration, price 
        FROM t_p5914469_beauty_salon_project.services 
        WHERE master_id = %s ORDER BY name
    """, (master_id,))
    services = cur.fetchall()
    cur.close()
    conn.close()
    
    keyboard = {'inline_keyboard': []}
    for s in services:
        keyboard['inline_keyboard'].append([
            {'text': f"{s['name']} — {s['duration']} мин, {s['price']}₽", 'callback_data': f"service_{s['id']}"}
        ])
    
    keyboard['inline_keyboard'].append([{'text': '« Назад', 'callback_data': 'back_to_masters'}])
    
    edit_message(chat_id, message_id, "💇 <b>Выберите услугу:</b>", keyboard)

def show_calendar(chat_id: int, message_id: int, service_id: int, year: int = None, month: int = None):
    """Показать календарь"""
    if not year or not month:
        now = datetime.now()
        year, month = now.year, now.month
    
    keyboard = build_calendar(year, month, service_id)
    edit_message(chat_id, message_id, "📅 <b>Выберите дату:</b>", keyboard)

def show_time_slots(chat_id: int, message_id: int, service_id: int, date: str):
    """Временные слоты"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT master_id, duration FROM t_p5914469_beauty_salon_project.services WHERE id = %s", (service_id,))
    service = cur.fetchone()
    master_id, duration = service['master_id'], service['duration']
    
    # Занятые слоты
    cur.execute("""
        SELECT booking_time, duration FROM t_p5914469_beauty_salon_project.bookings 
        WHERE master_id = %s AND booking_date = %s AND status != 'cancelled'
    """, (master_id, date))
    bookings = cur.fetchall()
    
    cur.execute("""
        SELECT block_start, block_end FROM t_p5914469_beauty_salon_project.master_blocks
        WHERE master_id = %s AND block_date = %s
    """, (master_id, date))
    blocks = cur.fetchall()
    
    cur.close()
    conn.close()
    
    occupied = []
    for b in bookings:
        start = datetime.strptime(str(b['booking_time']), '%H:%M:%S')
        end = start + timedelta(minutes=b['duration'])
        occupied.append((start, end))
    
    for b in blocks:
        start = datetime.strptime(str(b['block_start']), '%H:%M:%S')
        end = datetime.strptime(str(b['block_end']), '%H:%M:%S')
        occupied.append((start, end))
    
    keyboard = {'inline_keyboard': []}
    row = []
    
    start_time = datetime.strptime("09:00", '%H:%M')
    end_time = datetime.strptime("20:00", '%H:%M')
    current = start_time
    
    while current < end_time:
        slot_end = current + timedelta(minutes=duration)
        available = all(slot_end <= os or current >= oe for os, oe in occupied)
        
        if available:
            time_str = current.strftime('%H:%M')
            row.append({'text': time_str, 'callback_data': f"time_{service_id}_{date}_{time_str}"})
            if len(row) == 3:
                keyboard['inline_keyboard'].append(row)
                row = []
        
        current += timedelta(minutes=30)
    
    if row:
        keyboard['inline_keyboard'].append(row)
    
    year, month = date.split('-')[0], date.split('-')[1]
    keyboard['inline_keyboard'].append([{'text': '« К календарю', 'callback_data': f'back_to_calendar_{service_id}_{year}_{month}'}])
    
    if len(keyboard['inline_keyboard']) == 1:
        edit_message(chat_id, message_id, f"❌ На {date} нет свободных слотов")
    else:
        edit_message(chat_id, message_id, f"🕐 <b>Выберите время ({date}):</b>", keyboard)

def show_master_bookings_today(chat_id: int, message_id: int, master_id: int):
    """Записи мастера на сегодня"""
    today = datetime.now().date()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT b.id, b.client_name, b.client_phone, b.booking_time, s.name as service_name, b.duration, b.price
        FROM t_p5914469_beauty_salon_project.bookings b
        JOIN t_p5914469_beauty_salon_project.services s ON b.service_id = s.id
        WHERE b.master_id = %s AND b.booking_date = %s AND b.status = 'confirmed'
        ORDER BY b.booking_time
    """, (master_id, today))
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    
    if not bookings:
        text = "📅 <b>На сегодня записей нет</b>"
    else:
        text = f"📅 <b>Записи на {today.strftime('%d.%m.%Y')}:</b>\n\n"
        for b in bookings:
            text += f"🕐 {b['booking_time']} — {b['service_name']}\n"
            text += f"👤 {b['client_name']} ({b['client_phone']})\n"
            text += f"💰 {b['price']}₽\n\n"
    
    keyboard = {'inline_keyboard': [[{'text': '« Назад', 'callback_data': 'start'}]]}
    edit_message(chat_id, message_id, text, keyboard)

def show_master_all_bookings(chat_id: int, message_id: int, master_id: int):
    """Все будущие записи мастера"""
    today = datetime.now().date()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT b.id, b.client_name, b.client_phone, b.booking_date, b.booking_time, s.name as service_name, b.duration, b.price
        FROM t_p5914469_beauty_salon_project.bookings b
        JOIN t_p5914469_beauty_salon_project.services s ON b.service_id = s.id
        WHERE b.master_id = %s AND b.booking_date >= %s AND b.status = 'confirmed'
        ORDER BY b.booking_date, b.booking_time
        LIMIT 10
    """, (master_id, today))
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    
    if not bookings:
        text = "📋 <b>Будущих записей нет</b>"
    else:
        text = "📋 <b>Ближайшие записи:</b>\n\n"
        for b in bookings:
            text += f"📅 {b['booking_date'].strftime('%d.%m.%Y')} в {b['booking_time']}\n"
            text += f"💇 {b['service_name']}\n"
            text += f"👤 {b['client_name']} ({b['client_phone']})\n"
            text += f"💰 {b['price']}₽\n\n"
    
    keyboard = {'inline_keyboard': [[{'text': '« Назад', 'callback_data': 'start'}]]}
    edit_message(chat_id, message_id, text, keyboard)

def show_client_bookings(chat_id: int, message_id: int, telegram_id: int):
    """Записи клиента"""
    today = datetime.now().date()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT b.id, b.booking_date, b.booking_time, s.name as service_name, m.name as master_name, b.price
        FROM t_p5914469_beauty_salon_project.bookings b
        JOIN t_p5914469_beauty_salon_project.services s ON b.service_id = s.id
        JOIN t_p5914469_beauty_salon_project.masters m ON b.master_id = m.id
        WHERE b.telegram_id = %s AND b.booking_date >= %s AND b.status = 'confirmed'
        ORDER BY b.booking_date, b.booking_time
    """, (telegram_id, today))
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    
    if not bookings:
        text = "📋 <b>У вас нет активных записей</b>"
        keyboard = {'inline_keyboard': [
            [{'text': '📝 Записаться', 'callback_data': 'client_book'}]
        ]}
    else:
        text = "📋 <b>Ваши записи:</b>\n\n"
        for b in bookings:
            text += f"📅 {b['booking_date'].strftime('%d.%m.%Y')} в {b['booking_time']}\n"
            text += f"💇 {b['service_name']}\n"
            text += f"👤 Мастер: {b['master_name']}\n"
            text += f"💰 {b['price']}₽\n\n"
        
        keyboard = {'inline_keyboard': [
            [{'text': '📝 Новая запись', 'callback_data': 'client_book'}],
            [{'text': '« Назад', 'callback_data': 'start'}]
        ]}
    
    edit_message(chat_id, message_id, text, keyboard)

def request_client_data(chat_id: int, message_id: int, service_id: int, date: str, time: str):
    """Запрос данных клиента"""
    user = get_user_info(chat_id)
    
    if user['type'] == 'client':
        # Клиент уже известен, создаём запись сразу
        create_booking(chat_id, service_id, date, time, user['name'], user['phone'])
    else:
        # Новый клиент, запрашиваем данные
        save_session(chat_id, {'state': 'waiting_name', 'service_id': service_id, 'date': date, 'time': time})
        edit_message(chat_id, message_id, "✏️ Введите ваше имя:")

def create_booking(chat_id: int, service_id: int, date: str, time: str, name: str, phone: str):
    """Создание записи"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT master_id, name, price FROM t_p5914469_beauty_salon_project.services WHERE id = %s", (service_id,))
    service = cur.fetchone()
    
    cur.execute("""
        INSERT INTO t_p5914469_beauty_salon_project.bookings 
        (master_id, service_id, client_name, client_phone, booking_date, booking_time, duration, price, status, telegram_id)
        VALUES (%s, %s, %s, %s, %s, %s, 
            (SELECT duration FROM t_p5914469_beauty_salon_project.services WHERE id = %s),
            %s, 'confirmed', %s)
        RETURNING id
    """, (service['master_id'], service_id, name, phone, date, time, service_id, service['price'], chat_id))
    
    booking_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    
    save_session(chat_id, {})
    
    text = f"""✅ <b>Запись подтверждена!</b>

📋 {service['name']}
📅 {date}
🕐 {time}
💰 {service['price']}₽

👤 {name}
📱 {phone}

№{booking_id}"""
    
    keyboard = {'inline_keyboard': [[{'text': '📝 Новая запись', 'callback_data': 'client_book'}]]}
    send_message(chat_id, text, keyboard)

def handle_text_message(chat_id: int, text: str):
    """Обработка текста"""
    session = get_session(chat_id)
    state = session.get('state')
    
    if state == 'waiting_name':
        session['name'] = text
        session['state'] = 'waiting_phone'
        save_session(chat_id, session)
        send_message(chat_id, "📱 Введите ваш телефон:")
    
    elif state == 'waiting_phone':
        create_booking(chat_id, session['service_id'], session['date'], session['time'], session['name'], text)

def handle_callback_query(callback_query: dict):
    """Обработка callback"""
    data = callback_query['data']
    chat_id = callback_query['message']['chat']['id']
    message_id = callback_query['message']['message_id']
    callback_id = callback_query['id']
    user_id = callback_query['from']['id']
    
    answer_callback(callback_id)
    
    if data == 'ignore':
        return
    
    if data == 'start':
        username = callback_query['from'].get('username', '')
        show_main_menu(chat_id, user_id, username)
    
    elif data == 'client_book':
        show_masters(chat_id, message_id)
    
    elif data == 'client_bookings':
        show_client_bookings(chat_id, message_id, user_id)
    
    elif data == 'master_today':
        user = get_user_info(user_id)
        if user['type'] == 'master':
            show_master_bookings_today(chat_id, message_id, user['id'])
    
    elif data == 'master_all':
        user = get_user_info(user_id)
        if user['type'] == 'master':
            show_master_all_bookings(chat_id, message_id, user['id'])
    
    elif data == 'master_block':
        keyboard = {'inline_keyboard': [[{'text': '« Назад', 'callback_data': 'start'}]]}
        edit_message(chat_id, message_id, "⚠️ Функция блокировки времени в разработке", keyboard)
    
    elif data == 'back_to_masters':
        show_masters(chat_id, message_id)
    
    elif data.startswith('master_') and data not in ['master_today', 'master_all', 'master_block']:
        master_id = int(data.split('_')[1])
        save_session(chat_id, {'master_id': master_id})
        show_services(chat_id, message_id, master_id)
    
    elif data == 'back_to_services':
        session = get_session(chat_id)
        show_services(chat_id, message_id, session.get('master_id'))
    
    elif data.startswith('service_'):
        service_id = int(data.split('_')[1])
        show_calendar(chat_id, message_id, service_id)
    
    elif data.startswith('cal_prev_'):
        parts = data.split('_')
        year, month, service_id = int(parts[2]), int(parts[3]), int(parts[4])
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        show_calendar(chat_id, message_id, service_id, year, month)
    
    elif data.startswith('cal_next_'):
        parts = data.split('_')
        year, month, service_id = int(parts[2]), int(parts[3]), int(parts[4])
        month += 1
        if month > 12:
            month = 1
            year += 1
        show_calendar(chat_id, message_id, service_id, year, month)
    
    elif data.startswith('back_to_calendar_'):
        parts = data.split('_')
        service_id, year, month = int(parts[3]), int(parts[4]), int(parts[5])
        show_calendar(chat_id, message_id, service_id, year, month)
    
    elif data.startswith('date_'):
        parts = data.split('_')
        service_id = int(parts[1])
        date = parts[2]
        show_time_slots(chat_id, message_id, service_id, date)
    
    elif data.startswith('time_'):
        parts = data.split('_')
        service_id, date, time = int(parts[1]), parts[2], parts[3]
        request_client_data(chat_id, message_id, service_id, date, time)

def handler(event: dict, context) -> dict:
    """Telegram bot webhook"""
    print(f"[EVENT] {json.dumps(event, ensure_ascii=False)}")
    
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type'}, 'body': '', 'isBase64Encoded': False}
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        if 'callback_query' in body:
            handle_callback_query(body['callback_query'])
        
        elif 'message' in body:
            msg = body['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')
            user_id = msg['from']['id']
            
            username = msg['from'].get('username', '')
            
            if text == '/start':
                show_main_menu(chat_id, user_id, username)
            else:
                handle_text_message(chat_id, text)
        
        return response(200, {'ok': True})
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {'error': str(e)})