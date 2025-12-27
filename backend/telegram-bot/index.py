import json
import os
from typing import Dict, Any
import psycopg2
from datetime import datetime, timedelta

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Telegram бот для управления записями клиентов
    Позволяет мастеру просматривать расписание и добавлять клиентов
    """
    method: str = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Метод не поддерживается'})
        }
    
    update = json.loads(event.get('body', '{}'))
    
    if 'message' not in update:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'ok': True})
        }
    
    message = update['message']
    chat_id = message['chat']['id']
    text = message.get('text', '')
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    allowed_chat_ids = [
        os.environ.get('TELEGRAM_CHAT_ID'),
        os.environ.get('TELEGRAM_CHAT_ID_2'),
        os.environ.get('TELEGRAM_CHAT_ID_3'),
        os.environ.get('TELEGRAM_CHAT_ID_4'),
        os.environ.get('TELEGRAM_CHAT_ID_5')
    ]
    allowed_chat_ids = [cid for cid in allowed_chat_ids if cid]
    
    if str(chat_id) not in allowed_chat_ids:
        response_text = '⛔️ У вас нет доступа к этому боту'
        return send_telegram_message(bot_token, chat_id, response_text)
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    if text == '/start':
        response_text = """👋 Добро пожаловать в систему управления записями!

Доступные команды:
/today - Записи на сегодня
/tomorrow - Записи на завтра
/week - Записи на неделю
/add - Добавить клиента
/help - Помощь"""
        
    elif text == '/today':
        today = datetime.now().date()
        cur.execute(
            "SELECT id, master, client_name, client_phone, service, appointment_time FROM t_p5914469_beauty_salon_project.appointments WHERE appointment_date = %s ORDER BY appointment_time",
            (today,)
        )
        appointments = cur.fetchall()
        
        if not appointments:
            response_text = f"📅 На сегодня ({today.strftime('%d.%m.%Y')}) записей нет"
        else:
            response_text = f"📅 Записи на сегодня ({today.strftime('%d.%m.%Y')}):\n\n"
            for apt in appointments:
                response_text += f"🕐 {apt[5].strftime('%H:%M')} - {apt[1]}\n"
                response_text += f"👤 {apt[2]} ({apt[3]})\n"
                response_text += f"💅 {apt[4]}\n"
                response_text += f"ID: {apt[0]}\n\n"
    
    elif text == '/tomorrow':
        tomorrow = datetime.now().date() + timedelta(days=1)
        cur.execute(
            "SELECT id, master, client_name, client_phone, service, appointment_time FROM t_p5914469_beauty_salon_project.appointments WHERE appointment_date = %s ORDER BY appointment_time",
            (tomorrow,)
        )
        appointments = cur.fetchall()
        
        if not appointments:
            response_text = f"📅 На завтра ({tomorrow.strftime('%d.%m.%Y')}) записей нет"
        else:
            response_text = f"📅 Записи на завтра ({tomorrow.strftime('%d.%m.%Y')}):\n\n"
            for apt in appointments:
                response_text += f"🕐 {apt[5].strftime('%H:%M')} - {apt[1]}\n"
                response_text += f"👤 {apt[2]} ({apt[3]})\n"
                response_text += f"💅 {apt[4]}\n"
                response_text += f"ID: {apt[0]}\n\n"
    
    elif text == '/week':
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        cur.execute(
            "SELECT id, master, client_name, client_phone, service, appointment_date, appointment_time FROM t_p5914469_beauty_salon_project.appointments WHERE appointment_date BETWEEN %s AND %s ORDER BY appointment_date, appointment_time",
            (today, week_end)
        )
        appointments = cur.fetchall()
        
        if not appointments:
            response_text = "📅 На ближайшую неделю записей нет"
        else:
            response_text = "📅 Записи на неделю:\n\n"
            current_date = None
            for apt in appointments:
                if apt[5] != current_date:
                    current_date = apt[5]
                    response_text += f"\n📆 {current_date.strftime('%d.%m.%Y (%A)')}\n"
                response_text += f"🕐 {apt[6].strftime('%H:%M')} - {apt[1]}\n"
                response_text += f"👤 {apt[2]} ({apt[3]})\n"
                response_text += f"💅 {apt[4]}\n\n"
    
    elif text == '/add':
        response_text = """➕ Чтобы добавить клиента, отправьте сообщение в формате:

/new Имя | Телефон | Услуга | Дата | Время | Мастер

Пример:
/new Мария Иванова | +79001234567 | Маникюр | 25.12.2024 | 14:00 | Анна"""
    
    elif text.startswith('/new '):
        try:
            data = text[5:].strip()
            parts = [p.strip() for p in data.split('|')]
            
            if len(parts) < 6:
                response_text = "❌ Неверный формат. Используйте:\n/new Имя | Телефон | Услуга | Дата | Время | Мастер"
            else:
                client_name = parts[0]
                client_phone = parts[1]
                service = parts[2]
                date_str = parts[3]
                time_str = parts[4]
                master = parts[5]
                
                appointment_date = datetime.strptime(date_str, '%d.%m.%Y').date()
                appointment_time = datetime.strptime(time_str, '%H:%M').time()
                
                cur.execute(
                    "INSERT INTO t_p5914469_beauty_salon_project.appointments (master, client_name, client_phone, service, appointment_date, appointment_time, message) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (master, client_name, client_phone, service, appointment_date, appointment_time, 'Добавлено через бот')
                )
                apt_id = cur.fetchone()[0]
                conn.commit()
                
                response_text = f"✅ Клиент добавлен!\n\n"
                response_text += f"ID записи: {apt_id}\n"
                response_text += f"👤 {client_name}\n"
                response_text += f"📞 {client_phone}\n"
                response_text += f"💅 {service}\n"
                response_text += f"👨‍💼 Мастер: {master}\n"
                response_text += f"📅 {appointment_date.strftime('%d.%m.%Y')} в {appointment_time.strftime('%H:%M')}"
        except Exception as e:
            response_text = f"❌ Ошибка при добавлении: {str(e)}\n\nПроверьте формат данных"
    
    elif text == '/help':
        response_text = """📖 Справка по командам:

/today - Показать записи на сегодня
/tomorrow - Показать записи на завтра  
/week - Показать записи на неделю

/add - Инструкция по добавлению клиента
/new - Добавить клиента (см. /add для формата)

/help - Эта справка"""
    
    else:
        response_text = "❓ Неизвестная команда. Используйте /help для списка команд"
    
    cur.close()
    conn.close()
    
    return send_telegram_message(bot_token, chat_id, response_text)


def send_telegram_message(bot_token: str, chat_id: int, text: str) -> Dict[str, Any]:
    """Отправляет сообщение в Telegram"""
    import requests
    
    try:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        )
    except Exception:
        pass
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'isBase64Encoded': False,
        'body': json.dumps({'ok': True})
    }
