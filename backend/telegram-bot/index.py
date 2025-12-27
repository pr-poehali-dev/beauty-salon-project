import json
import os
from typing import Dict, Any
import psycopg2
from datetime import datetime, timedelta

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Telegram бот для управления записями и расписанием салона красоты
    - Клиенты могут смотреть свободные окна и записываться
    - Мастера могут управлять графиком работы и просматривать записи
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
    admin_chat_ids = [
        os.environ.get('TELEGRAM_CHAT_ID'),
        os.environ.get('TELEGRAM_CHAT_ID_2'),
        os.environ.get('TELEGRAM_CHAT_ID_3'),
        os.environ.get('TELEGRAM_CHAT_ID_4'),
        os.environ.get('TELEGRAM_CHAT_ID_5')
    ]
    admin_chat_ids = [cid for cid in admin_chat_ids if cid]
    is_admin = str(chat_id) in admin_chat_ids
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    if text == '/start':
        if is_admin:
            response_text = """👋 Добро пожаловать, мастер!

📋 Команды для мастеров:
/today - Записи на сегодня
/tomorrow - Записи на завтра
/week - Записи на неделю
/add - Добавить клиента

⚙️ Управление графиком:
/schedule - Посмотреть график работы
/addslot - Добавить рабочее время
/removeslot - Удалить рабочее время

/help - Полная справка"""
        else:
            response_text = """👋 Добро пожаловать в салон красоты!

💅 Доступные команды:
/free - Посмотреть свободные окна
/book - Записаться на услугу
/myappointments - Мои записи

/help - Помощь"""
        
    elif text == '/help':
        if is_admin:
            response_text = """📖 Справка для мастеров:

📋 Просмотр записей:
/today - Записи на сегодня
/tomorrow - Записи на завтра  
/week - Записи на неделю

➕ Добавление клиента:
/new Имя | Телефон | Услуга | Дата | Время | Мастер

Пример:
/new Мария | +79001234567 | Маникюр | 30.12.2024 | 14:00 | Анна

⚙️ Управление графиком:
/schedule - График работы
/addslot Дата | Время начала | Время конца | Мастер

Пример:
/addslot 30.12.2024 | 09:00 | 18:00 | Анна"""
        else:
            response_text = """📖 Справка для клиентов:

/free - Посмотреть свободные окна для записи
/book - Записаться на услугу

Для записи используйте формат:
/book Ваше Имя | Телефон | Услуга | Дата | Время | Мастер

Пример:
/book Анна Смирнова | +79001234567 | Маникюр | 30.12.2024 | 14:00 | Анна

/myappointments - Посмотреть ваши записи"""
    
    elif text == '/today' and is_admin:
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
    
    elif text == '/tomorrow' and is_admin:
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
    
    elif text == '/week' and is_admin:
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
                    response_text += f"\n📆 {current_date.strftime('%d.%m.%Y')}\n"
                response_text += f"🕐 {apt[6].strftime('%H:%M')} - {apt[1]}\n"
                response_text += f"👤 {apt[2]} ({apt[3]})\n"
                response_text += f"💅 {apt[4]}\n\n"
    
    elif text == '/add' and is_admin:
        response_text = """➕ Чтобы добавить клиента, отправьте сообщение в формате:

/new Имя | Телефон | Услуга | Дата | Время | Мастер

Пример:
/new Мария Иванова | +79001234567 | Маникюр | 30.12.2024 | 14:00 | Анна"""
    
    elif text.startswith('/new ') and is_admin:
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
                    "SELECT COUNT(*) FROM t_p5914469_beauty_salon_project.appointments WHERE appointment_date = %s AND appointment_time = %s AND master = %s",
                    (appointment_date, appointment_time, master)
                )
                if cur.fetchone()[0] > 0:
                    response_text = f"❌ На это время у мастера {master} уже есть запись!\nВыберите другое время."
                else:
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
    
    elif text == '/free':
        response_text = """💅 Свободные окна для записи:

📅 Чтобы посмотреть свободные окна, напишите:
/freeon Дата

Пример:
/freeon 30.12.2024

Доступные мастера:
• Анна
• Катя
• Света"""
    
    elif text.startswith('/freeon '):
        try:
            date_str = text[8:].strip()
            appointment_date = datetime.strptime(date_str, '%d.%m.%Y').date()
            
            cur.execute(
                "SELECT master, appointment_time FROM t_p5914469_beauty_salon_project.appointments WHERE appointment_date = %s ORDER BY master, appointment_time",
                (appointment_date,)
            )
            booked = cur.fetchall()
            
            masters = ['Анна', 'Катя', 'Света']
            work_hours = list(range(9, 19))
            
            response_text = f"💅 Свободные окна на {appointment_date.strftime('%d.%m.%Y')}:\n\n"
            
            for master in masters:
                booked_times = [b[1].hour for b in booked if b[0] == master]
                free_times = [h for h in work_hours if h not in booked_times]
                
                if free_times:
                    response_text += f"👤 {master}:\n"
                    for hour in free_times:
                        response_text += f"   {hour:02d}:00\n"
                    response_text += "\n"
            
            response_text += "Для записи используйте /book"
            
        except Exception as e:
            response_text = f"❌ Ошибка: {str(e)}\nИспользуйте формат: /freeon 30.12.2024"
    
    elif text.startswith('/book '):
        try:
            data = text[6:].strip()
            parts = [p.strip() for p in data.split('|')]
            
            if len(parts) < 6:
                response_text = "❌ Неверный формат. Используйте:\n/book Ваше Имя | Телефон | Услуга | Дата | Время | Мастер\n\nПример:\n/book Анна Смирнова | +79001234567 | Маникюр | 30.12.2024 | 14:00 | Анна"
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
                    "SELECT COUNT(*) FROM t_p5914469_beauty_salon_project.appointments WHERE appointment_date = %s AND appointment_time = %s AND master = %s",
                    (appointment_date, appointment_time, master)
                )
                if cur.fetchone()[0] > 0:
                    response_text = f"❌ К сожалению, это время уже занято!\n\nИспользуйте /freeon {date_str} чтобы посмотреть свободные окна"
                else:
                    cur.execute(
                        "INSERT INTO t_p5914469_beauty_salon_project.appointments (master, client_name, client_phone, service, appointment_date, appointment_time, message) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                        (master, client_name, client_phone, service, appointment_date, appointment_time, f'Запись через бот от клиента {chat_id}')
                    )
                    apt_id = cur.fetchone()[0]
                    conn.commit()
                    
                    response_text = f"✅ Вы успешно записаны!\n\n"
                    response_text += f"ID записи: {apt_id}\n"
                    response_text += f"👤 {client_name}\n"
                    response_text += f"💅 {service}\n"
                    response_text += f"👨‍💼 Мастер: {master}\n"
                    response_text += f"📅 {appointment_date.strftime('%d.%m.%Y')} в {appointment_time.strftime('%H:%M')}\n\n"
                    response_text += f"📞 Если нужно отменить или перенести, позвоните нам!"
                    
                    for admin_id in admin_chat_ids:
                        notify_text = f"🔔 Новая запись через бот!\n\n"
                        notify_text += f"👤 {client_name} ({client_phone})\n"
                        notify_text += f"💅 {service}\n"
                        notify_text += f"👨‍💼 Мастер: {master}\n"
                        notify_text += f"📅 {appointment_date.strftime('%d.%m.%Y')} в {appointment_time.strftime('%H:%M')}\n"
                        notify_text += f"ID: {apt_id}"
                        send_telegram_message_async(bot_token, admin_id, notify_text)
                        
        except Exception as e:
            response_text = f"❌ Ошибка при записи: {str(e)}\n\nПроверьте формат данных"
    
    elif text == '/myappointments':
        cur.execute(
            "SELECT id, master, service, appointment_date, appointment_time FROM t_p5914469_beauty_salon_project.appointments WHERE message LIKE %s AND appointment_date >= %s ORDER BY appointment_date, appointment_time",
            (f'%клиента {chat_id}%', datetime.now().date())
        )
        appointments = cur.fetchall()
        
        if not appointments:
            response_text = "📅 У вас пока нет записей"
        else:
            response_text = "📅 Ваши записи:\n\n"
            for apt in appointments:
                response_text += f"💅 {apt[2]}\n"
                response_text += f"👨‍💼 Мастер: {apt[1]}\n"
                response_text += f"📅 {apt[3].strftime('%d.%m.%Y')} в {apt[4].strftime('%H:%M')}\n"
                response_text += f"ID: {apt[0]}\n\n"
    
    else:
        if is_admin:
            response_text = "❓ Неизвестная команда. Используйте /help для списка команд"
        else:
            response_text = "❓ Неизвестная команда.\n\nДоступные команды:\n/free - Свободные окна\n/book - Записаться\n/myappointments - Мои записи\n/help - Помощь"
    
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


def send_telegram_message_async(bot_token: str, chat_id: str, text: str) -> None:
    """Отправляет сообщение в Telegram асинхронно (для уведомлений)"""
    import requests
    
    try:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'},
            timeout=2
        )
    except Exception:
        pass
