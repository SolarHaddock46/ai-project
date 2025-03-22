from database.database import add_event, delete_event, update_event, get_user_events_for_change
from datetime import datetime
import re
import streamlit as st

from dateparser import parse as date_parse
from typing import Optional

class EventTools:
    @staticmethod
    def _parse_datetime(datetime_str: str) -> Optional[str]:
        """
        Парсит абсолютные и относительные даты.
        Поддерживает форматы:
        - "завтра 14:00"
        - "через 3 дня"
        - "следующая пятница 16:30"
        - "15.04.2024 14:00" (старый формат)
        """
        try:
            # Пробуем распарсить относительную дату
            dt = date_parse(
                datetime_str,
                languages=['ru'],
                settings={'PREFER_DATES_FROM': 'future'}
            )

            # Если время не указано, используем 00:00
            if not dt.time():
                dt = dt.replace(hour=9, minute=0)  # Дефолтное время

            return dt.isoformat()

        except Exception as e:
            # Пробуем старый формат как fallback
            try:
                return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").isoformat()
            except:
                # Пробуем старый формат как последний fallback
                try:
                    return datetime.strptime(datetime_str, "%d.%m.%Y %H:%M").isoformat()
                except:
                    return None

    @staticmethod
    def add_event(title: str, start: str, end: str, description: str = "") -> dict:
        """Добавляет мероприятие в базу данных."""
        try:

            start_iso = EventTools._parse_datetime(start)
            # end_iso = EventTools._parse_datetime(end)
            end_iso = "2025-03-22T15:00:00"
            if not start_iso or not end_iso:
                return {"status": "error", "message": "Некорректный формат даты. Используйте 'дд.мм.гггг чч:мм'."}

            username = st.session_state["username"]
            add_event(username, title, start_iso, end_iso, description=description)
            return {"status": "success", "message": f"Мероприятие '{title}' добавлено."}
        except ValueError as e:
            return {"status": "error", "message": f"Некорректный формат времени: {str(e)}"}

    @staticmethod
    def delete_event(event_title: str) -> dict:
        """Удаляет мероприятие по названию."""
        username = st.session_state["username"]
        events = get_user_events_for_change(username)
        target_event = next((e for e in events if e["title"].lower() == event_title.lower()), None)
        if not target_event:
            return {"status": "error", "message": f"Мероприятие '{event_title}' не найдено."}

        delete_event(target_event["id"], username)
        return {"status": "success", "message": f"Мероприятие '{event_title}' удалено."}

    @staticmethod
    def get_events() -> str:
        """Возвращает список мероприятий в текстовом формате для RAG."""
        username = st.session_state["username"]
        events = get_user_events_for_change(username)
        return "\n".join([f"Мероприятие: {e['title']}, Начало: {e['start']}, Конец: {e['end']}" for e in events])


class CommandParser:
    @staticmethod
    def parse_llm_output(text: str) -> str:
        """Извлекает команды вида `add_event(...)` из текста LLM."""
        command_pattern = r'(add_event|delete_event|update_event)\(.*?\)'
        matches = re.findall(command_pattern, text)
        for match in matches:
            try:
                args = re.match(rf'{match}\((.*?)\)', text).group(1).split(', ')
                args = [a.strip('"') for a in args]
                if match == "add_event":
                    result = EventTools.add_event(args[0], args[1], args[2])
                elif match == "delete_event":
                    result = EventTools.delete_event(args[0])
                return result["message"]
            except Exception as e:
                return f"Ошибка выполнения команды: {str(e)}"
        return text  # Если команд нет, возвращаем исходный текст