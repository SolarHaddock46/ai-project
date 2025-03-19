import sqlite3
from datetime import datetime, timedelta
from hash.hash import hash_password

DB_NAME = "database/users.db"

def init_db():
    """Инициализация базы данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            start TEXT NOT NULL,
            end TEXT NOT NULL,
            color TEXT,
            description TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def adjust_timezone(iso_time_str: str, hours: int = -3) -> str:
    """Корректирует время в формате ISO."""
    dt = datetime.fromisoformat(iso_time_str.replace("Z", ""))
    adjusted_dt = dt + timedelta(hours=hours) if hours > 0 else dt - timedelta(hours=abs(hours))
    return adjusted_dt.strftime("%Y-%m-%dT%H:%M:%S")

def check_user(username: str, password_or_hash: str) -> bool:
    """Проверка пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        stored_hash = result[0]
        return stored_hash == (password_or_hash if len(password_or_hash) == 64 else hash_password(password_or_hash))
    return False

def register_user(username: str, password: str) -> bool:
    """Регистрация пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def add_event(username, title, start, end, color=None, description=None):
    """Добавление мероприятия в базу данных с корректировкой времени."""
    # Корректировка времени на -3 часа
    adjusted_start = start
    adjusted_end   = end
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (username, title, start, end, color, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, title, adjusted_start, adjusted_end, color, description))
    conn.commit()
    conn.close()

def update_event(event_id, username, title=None, start=None, end=None, color=None, description=None):
    """Редактирование мероприятия с корректировкой времени."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_event = get_event_by_id(event_id, username)
    if not current_event:
        conn.close()
        return False
    
    new_title = title if title is not None else current_event["title"]
    new_start = start if start is not None else current_event["start"]
    new_end = end if end is not None else current_event["end"]
    new_color = color if color is not None else current_event["color"]
    new_description = description if description is not None else current_event["description"]
    
    cursor.execute('''
        UPDATE events
        SET title=?, start=?, end=?, color=?, description=?
        WHERE id=? AND username=?
    ''', (new_title, new_start, new_end, new_color, new_description, event_id, username))
    conn.commit()
    conn.close()
    return True

def delete_event(event_id, username):
    """Удаление мероприятия."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id=? AND username=?", (event_id, username))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_user_events_for_render_calendar(username):
    """Получение всех мероприятий пользователя в формате streamlit-calendar."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, start, end, color, description FROM events WHERE username=?", (username,))
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        # Исправляем формат времени, убирая лишние :00
        start = row[2].replace(":00:00", ":00") if ":00:00" in row[2] else row[2]
        end = row[3].replace(":00:00", ":00") if ":00:00" in row[3] else row[3]
        
        event = {
            "title": row[1],
            "start": start,
            "end": end,
            "color": row[4],
            "description": row[5]
        }
        # Удаляем None-поля для совместимости с streamlit-calendar
        events.append({k: v for k, v in event.items() if v is not None})
    return events

def get_user_events_for_change(username):
    """Получение всех мероприятий пользователя с корректировкой времени (+3 часа)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, start, end, color, description FROM events WHERE username=?", (username,))
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        start = row[2]
        end = row[3]
        
        event = {
            "id": row[0],
            "title": row[1],
            "start": start,
            "end": end,
            "color": row[4],
            "description": row[5]
        }
        events.append({k: v for k, v in event.items() if v is not None or k == "id"})
    return events

def get_event_by_id(event_id, username):
    """Получение конкретного мероприятия по ID с корректировкой времени (+3 часа)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, start, end, color, description FROM events WHERE id=? AND username=?", 
                   (event_id, username))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        start = row[2]
        end = row[3]
        return {
            "id": row[0],
            "title": row[1],
            "start": start,
            "end": end,
            "color": row[4],
            "description": row[5]
        }
    return None

def find_event_by_details(username, title, start, end):
    """Поиск мероприятия по username, title, start и end с корректировкой времени (+3 часа)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # В базе хранится время с вычетом 3 часов, поэтому вычитаем их для поиска
    search_start = start
    search_end = end
    cursor.execute("""
        SELECT id, title, start, end, color, description 
        FROM events 
        WHERE username=? AND title=? AND start=? AND end=?
    """, (username, title, search_start.replace("+03:00", ":00"), search_end.replace("+03:00", ":00")))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        start = adjust_timezone(row[2], hours=3)
        end = adjust_timezone(row[3], hours=3)
        return {
            "id": row[0],
            "title": row[1],
            "start": start,
            "end": end,
            "color": row[4],
            "description": row[5]
        }
    return None

# Инициализация базы данных
init_db()