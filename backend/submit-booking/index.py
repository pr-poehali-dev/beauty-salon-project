import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import psycopg2
from pydantic import BaseModel, Field

class BookingRequest(BaseModel):
    """Модель данных заявки на бронирование"""
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    service: str = Field(..., min_length=1)
    message: str = ''

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Обрабатывает заявки на бронирование: сохраняет в базу данных и отправляет на email
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
    booking = BookingRequest(**body_data)
    
    # Сохранение в базу данных
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO t_p5914469_beauty_salon_project.bookings (name, phone, service, message) VALUES (%s, %s, %s, %s) RETURNING id",
        (booking.name, booking.phone, booking.service, booking.message)
    )
    booking_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    # Отправка email (если настроен SMTP)
    email_sent = False
    try:
        smtp_host = os.environ.get('SMTP_HOST')
        
        if smtp_host:
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            smtp_user = os.environ.get('SMTP_USER', '')
            smtp_password = os.environ.get('SMTP_PASSWORD', '')
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = 'danilakrivenko5@gmail.com, danilakrivenko40@gmail.com'
            msg['Subject'] = f'Новая заявка #{booking_id} от {booking.name}'
            
            body = f"""
Поступила новая заявка на бронирование:

Имя: {booking.name}
Телефон: {booking.phone}
Услуга: {booking.service}
Сообщение: {booking.message}
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
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'isBase64Encoded': False,
        'body': json.dumps({
            'success': True,
            'booking_id': booking_id,
            'email_sent': email_sent,
            'message': 'Заявка успешно отправлена'
        })
    }