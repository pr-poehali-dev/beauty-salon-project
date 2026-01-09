import json
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

def response(status_code: int, body: dict) -> dict:
    """Формирование ответа для Yandex Cloud Functions"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, ensure_ascii=False),
        'isBase64Encoded': False
    }

def get_db():
    """Подключение к БД"""
    return psycopg2.connect(DATABASE_URL)

def send_message(chat_id: int, text: str, keyboard: dict = None) -> dict:
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if keyboard:
        payload['reply_markup'] = keyboard
    
    resp = requests.post(url, json=payload)
    print(f"[TELEGRAM] sendMessage response: {resp.status_code} {resp.text}")
    return resp.json()

def edit_message(chat_id: int, message_id: int, text: str, keyboard: dict = None) -> dict:
    """Редактирование сообщения"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if keyboard:
        payload['reply_markup'] = keyboard
    
    resp = requests.post(url, json=payload)
    print(f"[TELEGRAM] editMessage response: {resp.status_code}")
    return resp.json()

def save_user_session(chat_id: int, data: dict):
    """Сохранение сессии пользователя"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO t_p5914469_beauty_salon_project.user_sessions (chat_id, session_data, updated_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (chat_id) 
        DO UPDATE SET session_data = %s, updated_at = NOW()
    """, (chat_id, json.dumps(data), json.dumps(data)))
    
    conn.commit()
    cur.close()
    conn.close()

def get_user_session(chat_id: int) -> dict:
    """Получение сессии пользователя"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        "SELECT session_data FROM t_p5914469_beauty_salon_project.user_sessions WHERE chat_id = %s",
        (chat_id,)
    )
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result and result['session_data']:
        return json.loads(result['session_data'])
    return {}

def send_masters_list(chat_id: int):
    """Отправка списка мастеров"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT id, name FROM t_p5914469_beauty_salon_project.masters ORDER BY name")
    masters = cur.fetchall()
    
    cur.close()
    conn.close()
    
    keyboard = {'inline_keyboard': []}
    for master in masters:
        keyboard['inline_keyboard'].append([
            {'text': master['name'], 'callback_data': f"master_{master['id']}"}
        ])
    
    send_message(chat_id, "👨‍💼 Выберите мастера:", keyboard)

def send_services_list(chat_id: int, message_id: int, master_id: int):
    """Отправка услуг выбранного мастера"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT id, name, duration, price 
        FROM t_p5914469_beauty_salon_project.services 
        WHERE master_id = %s 
        ORDER BY name
    """, (master_id,))
    services = cur.fetchall()
    
    cur.close()
    conn.close()
    
    keyboard = {'inline_keyboard': []}
    for service in services:
        text = f"{service['name']} ({service['duration']} мин, {service['price']}₽)"
        keyboard['inline_keyboard'].append([
            {'text': text, 'callback_data': f"service_{service['id']}"}
        ])
    
    keyboard['inline_keyboard'].append([{'text': '« Назад', 'callback_data': 'back_to_masters'}])
    
    edit_message(chat_id, message_id, "💇 Выберите услугу:", keyboard)

def send_dates(chat_id: int, message_id: int, service_id: int):
    """Отправка доступных дат"""
    keyboard = {'inline_keyboard': []}
    
    today = datetime.now()
    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        display = date.strftime('%d.%m (%a)')
        
        keyboard['inline_keyboard'].append([
            {'text': display, 'callback_data': f"date_{service_id}_{date_str}"}
        ])
    
    keyboard['inline_keyboard'].append([{'text': '« Назад', 'callback_data': 'back_to_services'}])
    
    edit_message(chat_id, message_id, "📅 Выберите дату:", keyboard)

def send_time_slots(chat_id: int, message_id: int, service_id: int, date: str):
    """Отправка доступного времени"""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Получаем данные услуги
    cur.execute(
        "SELECT master_id, duration FROM t_p5914469_beauty_salon_project.services WHERE id = %s",
        (service_id,)
    )
    service = cur.fetchone()
    master_id = service['master_id']
    duration = service['duration']
    
    # Получаем занятые слоты
    cur.execute("""
        SELECT booking_time, duration 
        FROM t_p5914469_beauty_salon_project.bookings 
        WHERE master_id = %s AND booking_date = %s AND status != 'cancelled'
    """, (master_id, date))
    bookings = cur.fetchall()
    
    # Получаем блокировки
    cur.execute("""
        SELECT block_start, block_end
        FROM t_p5914469_beauty_salon_project.master_blocks
        WHERE master_id = %s AND block_date = %s
    """, (master_id, date))
    blocks = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Формируем список занятых интервалов
    occupied = []
    
    for booking in bookings:
        start = datetime.strptime(str(booking['booking_time']), '%H:%M:%S')
        end = start + timedelta(minutes=booking['duration'])
        occupied.append((start, end))
    
    for block in blocks:
        start = datetime.strptime(str(block['block_start']), '%H:%M:%S')
        end = datetime.strptime(str(block['block_end']), '%H:%M:%S')
        occupied.append((start, end))
    
    # Генерируем слоты
    keyboard = {'inline_keyboard': []}
    row = []
    
    start_time = datetime.strptime("09:00", '%H:%M')
    end_time = datetime.strptime("20:00", '%H:%M')
    current = start_time
    
    while current < end_time:
        slot_end = current + timedelta(minutes=duration)
        
        # Проверяем доступность
        available = True
        for occ_start, occ_end in occupied:
            if not (slot_end <= occ_start or current >= occ_end):
                available = False
                break
        
        if available:
            time_str = current.strftime('%H:%M')
            row.append({'text': time_str, 'callback_data': f"time_{service_id}_{date}_{time_str}"})
            
            if len(row) == 3:
                keyboard['inline_keyboard'].append(row)
                row = []
        
        current += timedelta(minutes=30)
    
    if row:
        keyboard['inline_keyboard'].append(row)
    
    keyboard['inline_keyboard'].append([{'text': '« Назад', 'callback_data': f"back_to_dates_{service_id}"}])
    
    if len(keyboard['inline_keyboard']) == 1:
        edit_message(chat_id, message_id, f"❌ На {date} нет свободного времени")
    else:
        edit_message(chat_id, message_id, f"🕐 Выберите время на {date}:", keyboard)

def request_name(chat_id: int, message_id: int, service_id: int, date: str, time: str):
    """Запрос имени клиента"""
    save_user_session(chat_id, {
        'state': 'waiting_name',
        'service_id': service_id,
        'date': date,
        'time': time
    })
    
    edit_message(chat_id, message_id, "✏️ Введите ваше имя:")

def request_phone(chat_id: int, name: str):
    """Запрос телефона"""
    session = get_user_session(chat_id)
    session['state'] = 'waiting_phone'
    session['name'] = name
    save_user_session(chat_id, session)
    
    send_message(chat_id, "📱 Введите ваш телефон:")

def create_booking(chat_id: int, phone: str):
    """Создание записи"""
    session = get_user_session(chat_id)
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Получаем данные услуги
    cur.execute(
        "SELECT master_id, name, price FROM t_p5914469_beauty_salon_project.services WHERE id = %s",
        (session['service_id'],)
    )
    service = cur.fetchone()
    
    # Создаём запись
    cur.execute("""
        INSERT INTO t_p5914469_beauty_salon_project.bookings 
        (master_id, service_id, client_name, client_phone, booking_date, booking_time, duration, price, status)
        VALUES (%s, %s, %s, %s, %s, %s, 
            (SELECT duration FROM t_p5914469_beauty_salon_project.services WHERE id = %s),
            %s, 'confirmed')
        RETURNING id
    """, (
        service['master_id'],
        session['service_id'],
        session['name'],
        phone,
        session['date'],
        session['time'],
        session['service_id'],
        service['price']
    ))
    
    booking_id = cur.fetchone()['id']
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Очищаем сессию
    save_user_session(chat_id, {})
    
    # Отправляем подтверждение
    text = f"""
✅ <b>Запись подтверждена!</b>

📋 Услуга: {service['name']}
📅 Дата: {session['date']}
🕐 Время: {session['time']}
💰 Стоимость: {service['price']}₽

👤 {session['name']}
📱 {phone}

Номер записи: #{booking_id}
"""
    
    keyboard = {
        'inline_keyboard': [[
            {'text': '📝 Новая запись', 'callback_data': 'start'}
        ]]
    }
    
    send_message(chat_id, text, keyboard)

def handle_message(chat_id: int, text: str):
    """Обработка текстовых сообщений"""
    session = get_user_session(chat_id)
    state = session.get('state')
    
    if state == 'waiting_name':
        request_phone(chat_id, text)
    elif state == 'waiting_phone':
        create_booking(chat_id, text)
    else:
        send_masters_list(chat_id)

def handle_callback(chat_id: int, message_id: int, data: str):
    """Обработка callback кнопок"""
    print(f"[CALLBACK] {data}")
    
    if data == 'start' or data == 'back_to_masters':
        send_masters_list(chat_id)
    
    elif data.startswith('master_'):
        master_id = int(data.split('_')[1])
        save_user_session(chat_id, {'master_id': master_id})
        send_services_list(chat_id, message_id, master_id)
    
    elif data == 'back_to_services':
        session = get_user_session(chat_id)
        send_services_list(chat_id, message_id, session.get('master_id'))
    
    elif data.startswith('service_'):
        service_id = int(data.split('_')[1])
        send_dates(chat_id, message_id, service_id)
    
    elif data.startswith('back_to_dates_'):
        service_id = int(data.split('_')[3])
        send_dates(chat_id, message_id, service_id)
    
    elif data.startswith('date_'):
        parts = data.split('_')
        service_id = int(parts[1])
        date = parts[2]
        send_time_slots(chat_id, message_id, service_id, date)
    
    elif data.startswith('time_'):
        parts = data.split('_')
        service_id = int(parts[1])
        date = parts[2]
        time = parts[3]
        request_name(chat_id, message_id, service_id, date, time)

def handler(event: dict, context) -> dict:
    """Telegram bot webhook handler"""
    print(f"[REQUEST] {json.dumps(event, ensure_ascii=False)}")
    
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
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Обработка callback
        if 'callback_query' in body:
            callback = body['callback_query']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            data = callback['data']
            
            handle_callback(chat_id, message_id, data)
        
        # Обработка сообщения
        elif 'message' in body:
            message = body['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text == '/start':
                send_masters_list(chat_id)
            else:
                handle_message(chat_id, text)
        
        return response(200, {'ok': True})
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {'error': str(e)})
