import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Получает список всех заявок из базы данных
    Args: event - dict с httpMethod
          context - объект контекста выполнения
    Returns: HTTP ответ со списком заявок
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
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        "SELECT id, name, phone, service, message, created_at FROM t_p5914469_beauty_salon_project.bookings ORDER BY created_at DESC"
    )
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    
    bookings_list = []
    for booking in bookings:
        bookings_list.append({
            'id': booking['id'],
            'name': booking['name'],
            'phone': booking['phone'],
            'service': booking['service'],
            'message': booking['message'],
            'created_at': booking['created_at'].isoformat() if booking['created_at'] else None
        })
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'isBase64Encoded': False,
        'body': json.dumps({
            'success': True,
            'bookings': bookings_list,
            'total': len(bookings_list)
        })
    }
