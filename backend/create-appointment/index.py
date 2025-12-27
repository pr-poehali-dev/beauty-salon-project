import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import psycopg2
from pydantic import BaseModel, Field
import requests

class AppointmentRequest(BaseModel):
    """Модель данных записи к мастеру"""
    master: str = Field(..., min_length=1)
    client_name: str = Field(..., min_length=1)
    client_phone: str = Field(..., min_length=1)
    service: str = Field(..., min_length=1)
    appointment_date: str = Field(..., min_length=1)
    appointment_time: str = Field(..., min_length=1)
    message: str = ''

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Создает запись к мастеру на конкретное время
    Args: event - dict с httpMethod, body
          context - объект контекста выполнения
    Returns: HTTP ответ с результатом
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
    
    body_data = json.loads(event.get('body', '{}'))
    appointment = AppointmentRequest(**body_data)
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO t_p5914469_beauty_salon_project.appointments (master, client_name, client_phone, service, appointment_date, appointment_time, message) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
        (appointment.master, appointment.client_name, appointment.client_phone, appointment.service, appointment.appointment_date, appointment.appointment_time, appointment.message)
    )
    appointment_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    email_sent = False
    telegram_sent = False
    
    try:
        smtp_host = os.environ.get('SMTP_HOST')
        
        if smtp_host:
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            smtp_user = os.environ.get('SMTP_USER', '')
            smtp_password = os.environ.get('SMTP_PASSWORD', '')
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = 'danilakrivenko5@gmail.com, danilakrivenko40@gmail.com'
            msg['Subject'] = f'Новая запись #{appointment_id} к мастеру {appointment.master}'
            
            body = f"""
Новая запись к мастеру:

Мастер: {appointment.master}
Дата: {appointment.appointment_date}
Время: {appointment.appointment_time}

Клиент: {appointment.client_name}
Телефон: {appointment.client_phone}
Услуга: {appointment.service}
Сообщение: {appointment.message}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            email_sent = True
    except Exception:
        pass
    
    try:
        telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        telegram_chat_id_2 = os.environ.get('TELEGRAM_CHAT_ID_2')
        
        if telegram_bot_token and (telegram_chat_id or telegram_chat_id_2):
            telegram_message = f"""
🔔 Новая запись #{appointment_id}

👤 Мастер: {appointment.master}
📅 Дата: {appointment.appointment_date}
🕐 Время: {appointment.appointment_time}

👨‍💼 Клиент: {appointment.client_name}
📞 Телефон: {appointment.client_phone}
💅 Услуга: {appointment.service}
💬 Сообщение: {appointment.message}
            """
            
            if telegram_chat_id:
                requests.post(
                    f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage',
                    json={'chat_id': telegram_chat_id, 'text': telegram_message}
                )
            
            if telegram_chat_id_2:
                requests.post(
                    f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage',
                    json={'chat_id': telegram_chat_id_2, 'text': telegram_message}
                )
            
            telegram_sent = True
    except Exception:
        pass
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'isBase64Encoded': False,
        'body': json.dumps({
            'success': True,
            'appointment_id': appointment_id,
            'email_sent': email_sent,
            'telegram_sent': telegram_sent,
            'message': 'Запись успешно создана'
        })
    }