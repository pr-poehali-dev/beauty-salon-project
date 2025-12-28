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
    
    if 'callback_query' in update:
        callback = update['callback_query']
        chat_id = callback['message']['chat']['id']
        callback_data = callback.get('data', '')
        message_id = callback['message']['message_id']
        
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        if callback_data.startswith('cancel_'):
            apt_id = int(callback_data.split('_')[1])
            cur.execute("DELETE FROM appointments WHERE id = %s", (apt_id,))
            conn.commit()
            cur.close()
            conn.close()
            
            answer_callback_query(bot_token, callback['id'], "✅ Запись отменена")
            edit_message_text(bot_token, chat_id, message_id, f"✅ Запись #{apt_id} успешно отменена")
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True})
            }
        
        elif callback_data.startswith('book_date_'):
            selected_date = callback_data.split('_')[2]
            
            masters = ['Виктория', 'Алена']
            buttons = []
            for master in masters:
                buttons.append([{'text': f"👤 {master}", 'callback_data': f"book_master_{master}_{selected_date}"}])
            
            cur.close()
            conn.close()
            
            keyboard = {'inline_keyboard': buttons}
            edit_message_text_with_keyboard(bot_token, chat_id, message_id, f"📅 Выберите мастера на {datetime.strptime(selected_date, '%Y%m%d').strftime('%d.%m.%Y')}:", keyboard)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True})
            }
        
        elif callback_data.startswith('book_master_'):
            parts = callback_data.split('_')
            master = parts[2]
            selected_date = parts[3]
            
            cur.execute(
                "SELECT appointment_time FROM appointments WHERE appointment_date = %s AND master = %s ORDER BY appointment_time",
                (datetime.strptime(selected_date, '%Y%m%d').date(), master)
            )
            booked = cur.fetchall()
            
            work_hours = list(range(8, 22))
            booked_times = [b[0].hour for b in booked]
            free_times = [h for h in work_hours if h not in booked_times]
            
            buttons = []
            for hour in free_times:
                time_str = f"{hour:02d}:00"
                buttons.append([{'text': f"🕐 {time_str}", 'callback_data': f"book_time_{master}_{selected_date}_{hour:02d}00"}])
            
            cur.close()
            conn.close()
            
            if buttons:
                keyboard = {'inline_keyboard': buttons}
                edit_message_text_with_keyboard(bot_token, chat_id, message_id, f"🕐 Выберите время у мастера {master}:", keyboard)
            else:
                edit_message_text(bot_token, chat_id, message_id, f"❌ У мастера {master} нет свободных окон на {datetime.strptime(selected_date, '%Y%m%d').strftime('%d.%m.%Y')}")
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True})
            }
        
        elif callback_data.startswith('book_time_'):
            parts = callback_data.split('_')
            master = parts[2]
            selected_date = parts[3]
            time_str = parts[4]
            
            appointment_date = datetime.strptime(selected_date, '%Y%m%d').date()
            appointment_time = datetime.strptime(time_str, '%H%M').time()
            
            cur.execute(
                "SELECT COUNT(*) FROM appointments WHERE appointment_date = %s AND appointment_time = %s AND master = %s",
                (appointment_date, appointment_time, master)
            )
            if cur.fetchone()[0] > 0:
                answer_callback_query(bot_token, callback['id'], "❌ Это время уже занято")
                cur.close()
                conn.close()
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'ok': True})
                }
            
            cur.execute(
                "DELETE FROM appointments WHERE client_name LIKE %s AND service = 'temp'",
                (f'temp_{chat_id}%',)
            )
            
            cur.execute(
                "INSERT INTO appointments (master, client_name, client_phone, service, appointment_date, appointment_time, message) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (master, f'temp_{chat_id}', '', 'temp', appointment_date, appointment_time, f'step1_{chat_id}')
            )
            temp_apt_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            response_text = f"📝 Шаг 1 из 3: Введите ваше имя\n\n"
            response_text += f"Например: Анна Смирнова\n\n"
            response_text += f"📅 {master}, {appointment_date.strftime('%d.%m.%Y')} в {appointment_time.strftime('%H:%M')}"
            
            edit_message_text(bot_token, chat_id, message_id, response_text)
            answer_callback_query(bot_token, callback['id'], "✅ Введите ваше имя")
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True})
            }
        
        elif callback_data.startswith('service_'):
            service = callback_data.split('_', 1)[1]
            
            cur.execute(
                "SELECT id, master, appointment_date, appointment_time FROM appointments WHERE message LIKE %s AND service = 'temp'",
                (f'step3_{chat_id}%',)
            )
            pending = cur.fetchone()
            
            if pending:
                apt_id = pending[0]
                master = pending[1]
                appointment_date = pending[2]
                appointment_time = pending[3]
                
                cur.execute(
                    "SELECT client_name, client_phone FROM appointments WHERE id = %s",
                    (apt_id,)
                )
                client_data = cur.fetchone()
                client_name = client_data[0]
                client_phone = client_data[1]
                
                cur.execute(
                    "UPDATE appointments SET service = %s, message = %s WHERE id = %s",
                    (service, f'Запись через бот от клиента {chat_id}', apt_id)
                )
                conn.commit()
                
                admin_chat_ids = [
                    os.environ.get('TELEGRAM_CHAT_ID'),
                    os.environ.get('TELEGRAM_CHAT_ID_2'),
                    os.environ.get('TELEGRAM_CHAT_ID_3'),
                    os.environ.get('TELEGRAM_CHAT_ID_4'),
                    os.environ.get('TELEGRAM_CHAT_ID_5')
                ]
                admin_chat_ids = [cid for cid in admin_chat_ids if cid]
                
                response_text = f"✅ Вы успешно записаны!\n\n"
                response_text += f"ID записи: {apt_id}\n"
                response_text += f"👤 {client_name}\n"
                response_text += f"📞 {client_phone}\n"
                response_text += f"💅 {service}\n"
                response_text += f"👨‍💼 Мастер: {master}\n"
                response_text += f"📅 {appointment_date.strftime('%d.%m.%Y')} в {appointment_time.strftime('%H:%M')}\n\n"
                response_text += f"📋 Посмотреть записи: нажмите 📋 Мои записи"
                
                edit_message_text(bot_token, chat_id, message_id, response_text)
                answer_callback_query(bot_token, callback['id'], "✅ Запись создана!")
                
                for admin_id in admin_chat_ids:
                    notify_text = f"🔔 Новая запись через бот!\n\n"
                    notify_text += f"👤 {client_name} ({client_phone})\n"
                    notify_text += f"💅 {service}\n"
                    notify_text += f"👨‍💼 Мастер: {master}\n"
                    notify_text += f"📅 {appointment_date.strftime('%d.%m.%Y')} в {appointment_time.strftime('%H:%M')}\n"
                    notify_text += f"ID: {apt_id}"
                    send_telegram_message_async(bot_token, admin_id, notify_text)
            
            cur.close()
            conn.close()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True})
            }
    
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

Выберите действие с помощью кнопок ниже 👇"""
            keyboard = {
                'keyboard': [
                    [{'text': '📅 Записи на сегодня'}, {'text': '📅 Записи на завтра'}],
                    [{'text': '📅 Записи на неделю'}, {'text': '➕ Добавить клиента'}],
                    [{'text': '⚙️ График работы'}, {'text': '➕ Добавить слот'}],
                    [{'text': '🗑 Удалить слот'}, {'text': 'ℹ️ Помощь'}]
                ],
                'resize_keyboard': True,
                'one_time_keyboard': False
            }
            cur.close()
            conn.close()
            return send_telegram_message_with_keyboard(bot_token, chat_id, response_text, keyboard)
        else:
            response_text = """👋 Добро пожаловать в салон красоты!

Выберите действие с помощью кнопок ниже 👇"""
            keyboard = {
                'keyboard': [
                    [{'text': '💅 Свободные окна'}],
                    [{'text': '📋 Мои записи'}, {'text': 'ℹ️ Помощь'}]
                ],
                'resize_keyboard': True,
                'one_time_keyboard': False
            }
            cur.close()
            conn.close()
            return send_telegram_message_with_keyboard(bot_token, chat_id, response_text, keyboard)
        
    elif text == '/help' or text == 'ℹ️ Помощь':
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
    
    elif (text == '/today' or text == '📅 Записи на сегодня') and is_admin:
        today = datetime.now().date()
        cur.execute(
            "SELECT id, master, client_name, client_phone, service, appointment_time FROM appointments WHERE appointment_date = %s ORDER BY appointment_time",
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
    
    elif (text == '/tomorrow' or text == '📅 Записи на завтра') and is_admin:
        tomorrow = datetime.now().date() + timedelta(days=1)
        cur.execute(
            "SELECT id, master, client_name, client_phone, service, appointment_time FROM appointments WHERE appointment_date = %s ORDER BY appointment_time",
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
    
    elif (text == '/week' or text == '📅 Записи на неделю') and is_admin:
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        cur.execute(
            "SELECT id, master, client_name, client_phone, service, appointment_date, appointment_time FROM appointments WHERE appointment_date BETWEEN %s AND %s ORDER BY appointment_date, appointment_time",
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
    
    elif (text == '/add' or text == '➕ Добавить клиента') and is_admin:
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
                    "SELECT COUNT(*) FROM appointments WHERE appointment_date = %s AND appointment_time = %s AND master = %s",
                    (appointment_date, appointment_time, master)
                )
                if cur.fetchone()[0] > 0:
                    response_text = f"❌ На это время у мастера {master} уже есть запись!\nВыберите другое время."
                else:
                    cur.execute(
                        "INSERT INTO appointments (master, client_name, client_phone, service, appointment_date, appointment_time, message) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
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
    
    elif text == '/free' or text == '💅 Свободные окна':
        response_text = "💅 Выберите дату для записи:"
        
        today = datetime.now().date()
        buttons = []
        weekdays_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for i in range(7):
            date = today + timedelta(days=i)
            weekday = weekdays_ru[date.weekday()]
            date_str = date.strftime(f'%d.%m ({weekday})')
            buttons.append([{'text': date_str, 'callback_data': f"book_date_{date.strftime('%Y%m%d')}"}])
        
        keyboard = {'inline_keyboard': buttons}
        cur.close()
        conn.close()
        return send_telegram_message_with_inline_keyboard(bot_token, chat_id, response_text, keyboard)
    
    elif text.startswith('/freeon '):
        try:
            date_str = text[8:].strip()
            appointment_date = datetime.strptime(date_str, '%d.%m.%Y').date()
            
            cur.execute(
                "SELECT master, appointment_time FROM appointments WHERE appointment_date = %s ORDER BY master, appointment_time",
                (appointment_date,)
            )
            booked = cur.fetchall()
            
            masters = ['Виктория', 'Алена']
            work_hours = list(range(8, 22))
            
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
                    "SELECT COUNT(*) FROM appointments WHERE appointment_date = %s AND appointment_time = %s AND master = %s",
                    (appointment_date, appointment_time, master)
                )
                if cur.fetchone()[0] > 0:
                    response_text = f"❌ К сожалению, это время уже занято!\n\nИспользуйте /freeon {date_str} чтобы посмотреть свободные окна"
                else:
                    cur.execute(
                        "INSERT INTO appointments (master, client_name, client_phone, service, appointment_date, appointment_time, message) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
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
    
    elif text == '/myappointments' or text == '📋 Мои записи':
        cur.execute(
            "SELECT id, master, service, appointment_date, appointment_time FROM appointments WHERE message LIKE %s AND appointment_date >= %s ORDER BY appointment_date, appointment_time",
            (f'%клиента {chat_id}%', datetime.now().date())
        )
        appointments = cur.fetchall()
        
        if not appointments:
            response_text = "📅 У вас пока нет записей"
        else:
            response_text = "📅 Ваши записи:\n\n"
            buttons = []
            for apt in appointments:
                response_text += f"💅 {apt[2]}\n"
                response_text += f"👨‍💼 Мастер: {apt[1]}\n"
                response_text += f"📅 {apt[3].strftime('%d.%m.%Y')} в {apt[4].strftime('%H:%M')}\n"
                response_text += f"ID: {apt[0]}\n\n"
                buttons.append([{'text': f"❌ Отменить запись #{apt[0]}", 'callback_data': f"cancel_{apt[0]}"}])
            
            keyboard = {'inline_keyboard': buttons}
            cur.close()
            conn.close()
            return send_telegram_message_with_inline_keyboard(bot_token, chat_id, response_text, keyboard)
    
    elif (text == '/schedule' or text == '⚙️ График работы') and is_admin:
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        cur.execute(
            "SELECT master, work_date, start_time, end_time FROM work_schedule WHERE work_date BETWEEN %s AND %s ORDER BY work_date, master, start_time",
            (today, week_end)
        )
        schedule = cur.fetchall()
        
        if not schedule:
            response_text = "📅 График работы на неделю не установлен\n\nИспользуйте /addslot для добавления рабочего времени"
        else:
            response_text = "📅 График работы на неделю:\n\n"
            current_date = None
            for item in schedule:
                if item[1] != current_date:
                    current_date = item[1]
                    response_text += f"\n📆 {current_date.strftime('%d.%m.%Y')}\n"
                response_text += f"👤 {item[0]}: {item[2].strftime('%H:%M')} - {item[3].strftime('%H:%M')}\n"
    
    elif (text == '/addslot' or text == '➕ Добавить слот') and is_admin:
        response_text = """➕ Добавить рабочее время:

Формат:
/addslot Дата | Время начала | Время конца | Мастер

Пример:
/addslot 30.12.2024 | 09:00 | 18:00 | Анна

Или добавить на всю неделю:
/addslot 30.12.2024-05.01.2025 | 09:00 | 18:00 | Анна"""
    
    elif text.startswith('/addslot ') and is_admin:
        try:
            data = text[9:].strip()
            parts = [p.strip() for p in data.split('|')]
            
            if len(parts) < 4:
                response_text = "❌ Неверный формат. Используйте:\n/addslot Дата | Время начала | Время конца | Мастер"
            else:
                date_str = parts[0]
                start_time_str = parts[1]
                end_time_str = parts[2]
                master = parts[3]
                
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
                
                dates_to_add = []
                if '-' in date_str:
                    date_parts = date_str.split('-')
                    start_date = datetime.strptime(date_parts[0].strip(), '%d.%m.%Y').date()
                    end_date = datetime.strptime(date_parts[1].strip(), '%d.%m.%Y').date()
                    current = start_date
                    while current <= end_date:
                        dates_to_add.append(current)
                        current += timedelta(days=1)
                else:
                    dates_to_add.append(datetime.strptime(date_str, '%d.%m.%Y').date())
                
                added_count = 0
                for work_date in dates_to_add:
                    try:
                        cur.execute(
                            "INSERT INTO work_schedule (master, work_date, start_time, end_time) VALUES (%s, %s, %s, %s)",
                            (master, work_date, start_time, end_time)
                        )
                        added_count += 1
                    except Exception:
                        pass
                
                conn.commit()
                
                if added_count > 0:
                    response_text = f"✅ Добавлено {added_count} рабочих дней для {master}\n\n"
                    response_text += f"⏰ {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
                else:
                    response_text = "⚠️ Эти слоты уже существуют в графике"
                    
        except Exception as e:
            response_text = f"❌ Ошибка: {str(e)}\n\nПроверьте формат данных"
    
    elif (text == '/removeslot' or text == '🗑 Удалить слот') and is_admin:
        response_text = """🗑 Удалить рабочее время:

Формат:
/removeslot Дата | Мастер

Пример:
/removeslot 30.12.2024 | Анна

Или удалить все слоты мастера на дату:
/removeslot 30.12.2024 | Анна"""
    
    elif text.startswith('/removeslot ') and is_admin:
        try:
            data = text[12:].strip()
            parts = [p.strip() for p in data.split('|')]
            
            if len(parts) < 2:
                response_text = "❌ Неверный формат. Используйте:\n/removeslot Дата | Мастер"
            else:
                date_str = parts[0]
                master = parts[1]
                
                work_date = datetime.strptime(date_str, '%d.%m.%Y').date()
                
                cur.execute(
                    "DELETE FROM work_schedule WHERE master = %s AND work_date = %s",
                    (master, work_date)
                )
                deleted_count = cur.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    response_text = f"✅ Удалено {deleted_count} рабочих слотов для {master} на {work_date.strftime('%d.%m.%Y')}"
                else:
                    response_text = f"⚠️ Рабочие слоты не найдены для {master} на {work_date.strftime('%d.%m.%Y')}"
                    
        except Exception as e:
            response_text = f"❌ Ошибка: {str(e)}\n\nПроверьте формат данных"
    
    else:
        if not is_admin:
            cur.execute(
                "SELECT id, master, appointment_date, appointment_time, message FROM appointments WHERE message LIKE %s AND service = 'temp'",
                (f'step%_{chat_id}',)
            )
            pending = cur.fetchone()
            
            if pending:
                apt_id = pending[0]
                master = pending[1]
                appointment_date = pending[2]
                appointment_time = pending[3]
                step_message = pending[4]
                
                if step_message.startswith(f'step1_{chat_id}'):
                    client_name = text.strip()
                    
                    cur.execute(
                        "UPDATE appointments SET client_name = %s, message = %s WHERE id = %s",
                        (client_name, f'step2_{chat_id}', apt_id)
                    )
                    conn.commit()
                    
                    response_text = f"📝 Шаг 2 из 3: Введите ваш телефон\n\n"
                    response_text += f"Например: +79001234567\n\n"
                    response_text += f"👤 {client_name}\n"
                    response_text += f"📅 {master}, {appointment_date.strftime('%d.%m.%Y')} в {appointment_time.strftime('%H:%M')}"
                
                elif step_message.startswith(f'step2_{chat_id}'):
                    client_phone = text.strip()
                    
                    cur.execute(
                        "UPDATE appointments SET client_phone = %s, message = %s WHERE id = %s",
                        (client_phone, f'step3_{chat_id}', apt_id)
                    )
                    conn.commit()
                    
                    cur.execute("SELECT client_name FROM appointments WHERE id = %s", (apt_id,))
                    client_name = cur.fetchone()[0]
                    
                    services = [
                        'Маникюр', 'Педикюр', 'Маникюр + Педикюр',
                        'Наращивание ногтей', 'Покрытие гель-лак',
                        'Снятие покрытия', 'Дизайн ногтей',
                        'Парафинотерапия', 'SPA-уход для рук/ног'
                    ]
                    
                    buttons = []
                    for service in services:
                        buttons.append([{'text': service, 'callback_data': f'service_{service}'}])
                    
                    keyboard = {'inline_keyboard': buttons}
                    cur.close()
                    conn.close()
                    
                    response_text = f"📝 Шаг 3 из 3: Выберите услугу\n\n"
                    response_text += f"👤 {client_name}\n"
                    response_text += f"📞 {client_phone}\n"
                    response_text += f"📅 {master}, {appointment_date.strftime('%d.%m.%Y')} в {appointment_time.strftime('%H:%M')}"
                    
                    return send_telegram_message_with_inline_keyboard(bot_token, chat_id, response_text, keyboard)
                
                else:
                    response_text = "❓ Неизвестная команда.\n\nДоступные команды:\n💅 Свободные окна\n📋 Мои записи\nℹ️ Помощь"
            else:
                response_text = "❓ Неизвестная команда.\n\nДоступные команды:\n💅 Свободные окна\n📋 Мои записи\nℹ️ Помощь"
        else:
            if is_admin:
                response_text = "❓ Неизвестная команда. Используйте /help для списка команд"
            else:
                response_text = "❓ Неизвестная команда.\n\nДоступные команды:\n💅 Свободные окна\n📋 Мои записи\nℹ️ Помощь"
    
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


def send_telegram_message_with_keyboard(bot_token: str, chat_id: int, text: str, keyboard: dict) -> Dict[str, Any]:
    """Отправляет сообщение в Telegram с клавиатурой"""
    import requests
    
    try:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'reply_markup': keyboard}
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


def send_telegram_message_with_inline_keyboard(bot_token: str, chat_id: int, text: str, keyboard: dict) -> Dict[str, Any]:
    """Отправляет сообщение в Telegram с inline клавиатурой"""
    import requests
    
    try:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'reply_markup': keyboard}
        )
    except Exception:
        pass
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'isBase64Encoded': False,
        'body': json.dumps({'ok': True})
    }


def answer_callback_query(bot_token: str, callback_query_id: str, text: str) -> None:
    """Отвечает на callback query"""
    import requests
    
    try:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/answerCallbackQuery',
            json={'callback_query_id': callback_query_id, 'text': text}
        )
    except Exception:
        pass


def edit_message_text(bot_token: str, chat_id: int, message_id: int, text: str) -> None:
    """Редактирует текст сообщения"""
    import requests
    
    try:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/editMessageText',
            json={'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'HTML'}
        )
    except Exception:
        pass


def edit_message_text_with_keyboard(bot_token: str, chat_id: int, message_id: int, text: str, keyboard: dict) -> None:
    """Редактирует текст сообщения с клавиатурой"""
    import requests
    
    try:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/editMessageText',
            json={'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'HTML', 'reply_markup': keyboard}
        )
    except Exception:
        pass