import json
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor


def handler(event: dict, context) -> dict:
    """Telegram бот для записи клиентов с проверкой времени процедур"""
    
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
            
            if 'message' in update:
                return handle_message(update['message'])
            elif 'callback_query' in update:
                return handle_callback(update['callback_query'])
            
            return response(200, {'ok': True})
            
        except Exception as e:
            return response(500, {'error': str(e)})
    
    return response(405, {'error': 'Method not allowed'})


def handle_message(message: dict) -> dict:
    """Обработка текстовых сообщений"""
    chat_id = message['chat']['id']
    text = message.get('text', '')
    
    if text == '/start':
        return send_welcome(chat_id)
    elif text == '/book':
        return send_masters_list(chat_id)
    
    return response(200, {'ok': True})


def handle_callback(callback: dict) -> dict:
    """Обработка нажатий на кнопки"""
    chat_id = callback['message']['chat']['id']
    message_id = callback['message']['message_id']
    data = callback['data']
    callback_id = callback['id']
    
    answer_callback(callback_id)
    
    if data == 'noop':
        return response(200, {'ok': True})
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
        return send_time_selection(chat_id, message_id, service_id, date)
    elif data.startswith('time_'):
        parts = data.split('_')
        service_id = int(parts[1])
        date = parts[2]
        time = parts[3]
        return confirm_booking(chat_id, message_id, service_id, date, time, callback['from'])
    
    return response(200, {'ok': True})


def send_welcome(chat_id: int) -> dict:
    """Приветственное сообщение"""
    text = """👋 Добро пожаловать в студию красоты!

Здесь вы можете записаться на услуги:
• Виктория — Ногтевой сервис
• Алёна — Шугаринг и уход за лицом

Нажмите /book для записи"""
    
    try:
        send_message(chat_id, text)
    except:
        pass
    return response(200, {'ok': True})


def send_masters_list(chat_id: int) -> dict:
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
    
    send_message(chat_id, "Выберите мастера:", keyboard)
    return response(200, {'ok': True})


def send_services_list(chat_id: int, message_id: int, master_id: int) -> dict:
    """Список услуг мастера"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
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
        
        text = f"{service['name']} — {service['price']}"
        keyboard['inline_keyboard'].append([{'text': text, 'callback_data': f"service_{service['id']}"}])
    
    edit_message(chat_id, message_id, "Выберите услугу:", keyboard)
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
    """Доступное время с учётом длительности процедур"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT master_id, duration FROM t_p5914469_beauty_salon_project.services WHERE id = %s", (service_id,))
    service = cur.fetchone()
    master_id = service['master_id']
    service_duration = service['duration']
    
    cur.execute("""
        SELECT booking_time, duration 
        FROM t_p5914469_beauty_salon_project.bookings 
        WHERE master_id = %s AND booking_date = %s AND status != 'cancelled'
        ORDER BY booking_time
    """, (master_id, date))
    bookings = cur.fetchall()
    
    cur.close()
    conn.close()
    
    occupied_slots = []
    for booking in bookings:
        start = datetime.strptime(str(booking['booking_time']), '%H:%M:%S')
        duration = booking['duration']
        end = start + timedelta(minutes=duration)
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


def confirm_booking(chat_id: int, message_id: int, service_id: int, date: str, time: str, user: dict) -> dict:
    """Подтверждение записи"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT s.name, s.price, s.duration, s.master_id, m.name as master_name
        FROM t_p5914469_beauty_salon_project.services s
        JOIN t_p5914469_beauty_salon_project.masters m ON s.master_id = m.id
        WHERE s.id = %s
    """, (service_id,))
    service = cur.fetchone()
    
    client_name = (user.get('first_name', '') + ' ' + user.get('last_name', '')).strip()
    client_telegram_id = str(user.get('id', ''))
    
    cur.execute("""
        INSERT INTO t_p5914469_beauty_salon_project.bookings 
        (master_id, service_id, client_name, client_phone, client_telegram_id, booking_date, booking_time, duration, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'confirmed')
        RETURNING id
    """, (service['master_id'], service_id, client_name, '', client_telegram_id, date, time, service['duration']))
    
    booking_id = cur.fetchone()['id']
    conn.commit()
    
    cur.close()
    conn.close()
    
    end_time = (datetime.strptime(time, '%H:%M') + timedelta(minutes=service['duration'])).strftime('%H:%M')
    
    text = f"""✅ Запись подтверждена!

Мастер: {service['master_name']}
Услуга: {service['name']}
Цена: {service['price']}
Дата: {date}
Время: {time}

Номер записи: #{booking_id}

Ждём вас! 💕"""
    
    edit_message(chat_id, message_id, text)
    notify_admins(service['master_name'], client_name, service['name'], date, time, end_time, booking_id)
    
    return response(200, {'ok': True})


def notify_admins(master: str, client: str, service: str, date: str, start: str, end: str, booking_id: int) -> None:
    """Уведомление администраторов"""
    text = f"""🔔 Новая запись!

Мастер: {master}
Клиент: {client}
Услуга: {service}
Дата: {date}
Время: {start} - {end}

Запись #{booking_id}"""
    
    for i in range(1, 6):
        chat_id = os.environ.get(f'TELEGRAM_CHAT_ID{"" if i == 1 else f"_{i}"}')
        if chat_id:
            send_message(chat_id, text)


def send_message(chat_id: str, text: str, keyboard=None) -> None:
    """Отправка сообщения"""
    import urllib.request
    import urllib.parse
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    
    data = {'chat_id': chat_id, 'text': text}
    if keyboard:
        data['reply_markup'] = json.dumps(keyboard)
    
    req = urllib.request.Request(url, urllib.parse.urlencode(data).encode(), method='POST')
    urllib.request.urlopen(req)


def edit_message(chat_id: int, message_id: int, text: str, keyboard=None) -> None:
    """Редактирование сообщения"""
    import urllib.request
    import urllib.parse
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    url = f'https://api.telegram.org/bot{token}/editMessageText'
    
    data = {'chat_id': chat_id, 'message_id': message_id, 'text': text}
    if keyboard:
        data['reply_markup'] = json.dumps(keyboard)
    
    req = urllib.request.Request(url, urllib.parse.urlencode(data).encode(), method='POST')
    urllib.request.urlopen(req)


def answer_callback(callback_id: str) -> None:
    """Ответ на callback query"""
    import urllib.request
    import urllib.parse
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    url = f'https://api.telegram.org/bot{token}/answerCallbackQuery'
    
    data = {'callback_query_id': callback_id}
    
    try:
        req = urllib.request.Request(url, urllib.parse.urlencode(data).encode(), method='POST')
        urllib.request.urlopen(req)
    except:
        pass


def get_db():
    """Подключение к БД"""
    return psycopg2.connect(os.environ.get('DATABASE_URL'))


def response(status: int, body: dict) -> dict:
    """Форматирование ответа"""
    return {
        'statusCode': status,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(body),
        'isBase64Encoded': False
    }