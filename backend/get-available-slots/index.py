import json
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta, time
import psycopg2

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Получает доступные временные слоты для записи к мастеру
    Args: event - dict с httpMethod, queryStringParameters (master, date)
          context - объект контекста выполнения
    Returns: HTTP ответ со списком свободных слотов
    """
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method != 'GET':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Метод не поддерживается'})
        }
    
    params = event.get('queryStringParameters', {}) or {}
    master = params.get('master', '')
    date_str = params.get('date', '')
    
    if not master or not date_str:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Укажите мастера и дату'})
        }
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    cur.execute(
        "SELECT appointment_time FROM t_p5914469_beauty_salon_project.appointments WHERE master = %s AND appointment_date = %s",
        (master, date_str)
    )
    booked_times = [row[0].strftime('%H:%M') for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    start_time = time(8, 0)
    end_time = time(22, 0)
    slot_duration = 60
    
    all_slots: List[str] = []
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)
    
    while current < end:
        time_slot = current.strftime('%H:%M')
        all_slots.append(time_slot)
        current += timedelta(minutes=slot_duration)
    
    available_slots = [slot for slot in all_slots if slot not in booked_times]
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'isBase64Encoded': False,
        'body': json.dumps({
            'success': True,
            'master': master,
            'date': date_str,
            'available_slots': available_slots
        })
    }
