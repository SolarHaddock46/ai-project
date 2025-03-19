import streamlit as st
from streamlit_calendar import calendar
import datetime
from ui.sidebar import render_sidebar
from database.database import (
    check_user, 
    get_user_events_for_render_calendar, 
    find_event_by_details, 
    update_event, 
    delete_event, 
    add_event
)

# Константы
CALENDAR_CONFIG = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "initialView": "dayGridMonth",
    "locale": "ru",
    "firstDay": 1
}

# Настройка страницы
st.set_page_config(
    page_title="Календарь мероприятий",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def setup_page():
    """Настройка базовых элементов страницы"""
    render_sidebar()
    if not st.session_state.get("username"):
        st.warning("Пожалуйста, войдите в систему для доступа к календарю.")
        st.page_link("app.py", label="Перейти к входу")
        return False
    st.title("📅 Календарь мероприятий")
    return True


def format_datetime(iso_string: str, timezone_offset: int = 0) -> str:
    """Форматирование ISO даты в читаемый вид"""
    dt = datetime.datetime.fromisoformat(iso_string[:19])
    return dt.strftime("%d %B %Y г., %H:%M")


def add_event_form(selected_date: str):
    """Форма для добавления мероприятия с использованием выбранной даты"""
    date_obj = datetime.datetime.fromisoformat(selected_date[:19]) + datetime.timedelta(hours=3)
    default_date = date_obj.date()
    
    st.subheader("Добавить мероприятие")
    with st.form(key="add_event_form"):
        title = st.text_input("Название мероприятия")
        start_date = st.date_input("Дата начала", value=default_date)
        start_time = st.time_input("Время начала", value=datetime.time(9, 0))
        end_date = st.date_input("Дата окончания", value=default_date)
        end_time = st.time_input("Время окончания", value=datetime.time(10, 0))
        color = st.color_picker("Цвет", value="#FF6C6C")
        description = st.text_area("Описание")
        submit = st.form_submit_button("Добавить")

        if submit:
            if not title:
                st.error("Название мероприятия обязательно!")
                return
            start = f"{start_date}T{start_time}:00"
            end = f"{end_date}T{end_time}:00"
            start_dt = datetime.datetime.fromisoformat(start)
            end_dt = datetime.datetime.fromisoformat(end)
            if start_dt > end_dt:
                st.error("Дата и время окончания не могут быть раньше даты и времени начала.")
                return
            username = st.session_state["username"]
            add_event(username, title, start, end, color, description)
            st.success("Мероприятие добавлено!")
            st.rerun()


def display_date_selection(selected_date: str):
    """Отображение информации о выбранной дате и формы добавления"""
    date_obj = datetime.datetime.fromisoformat(selected_date[:19]) + datetime.timedelta(hours=3)
    formatted_date = date_obj.strftime("%d %B %Y г.")
    
    st.write(f"Выбрана дата: **{formatted_date}**")
    if st.button("Добавить мероприятие"):
        st.session_state["selected_date"] = selected_date
    
    if "selected_date" in st.session_state and st.session_state["selected_date"] == selected_date:
        add_event_form(selected_date)


def edit_event_form(event):
    """Форма для редактирования мероприятия"""
    username = st.session_state["username"]
    event_details = find_event_by_details(username, event["title"], event["start"], event["end"])
    if not event_details:
        st.error("Мероприятие не найдено в базе данных!")
        return

    with st.form(key=f"edit_event_form_{event['title']}_{event['start']}"):
        title = st.text_input("Название мероприятия", value=event["title"])
        start_dt = datetime.datetime.fromisoformat(event["start"])
        start_date = st.date_input("Дата начала", value=start_dt.date())
        start_time = st.time_input("Время начала", value=start_dt.time())
        end_dt = datetime.datetime.fromisoformat(event["end"]) if "end" in event else start_dt
        end_date = st.date_input("Дата окончания", value=end_dt.date())
        end_time = st.time_input("Время окончания", value=end_dt.time())
        color = st.color_picker("Цвет", value=event.get("color", "#FF6C6C"))
        description = st.text_area(
            "Описание", 
            value=event.get("extendedProps", {}).get("description", event.get("description", "Описание отсутствует"))
        )
        submit = st.form_submit_button("Сохранить изменения")

        if submit:
            if not title:
                st.error("Название мероприятия обязательно!")
                return
            new_start = f"{start_date}T{start_time}:00"
            new_end = f"{end_date}T{end_time}:00"
            start_dt = datetime.datetime.fromisoformat(new_start)
            end_dt = datetime.datetime.fromisoformat(new_end)
            if start_dt > end_dt:
                st.error("Дата и время окончания не могут быть раньше даты и времени начала.")
                return
            update_event(event_details["id"], username, title, new_start, new_end, color, description)
            st.success("Мероприятие обновлено!")
            st.session_state["editing_event"] = None
            st.rerun()


def display_event_details(event: dict):
    """Отображение деталей выбранного события"""
    title = event.get("title", "Без названия")
    start = format_datetime(event["start"].replace("+03:00", "")) if "start" in event else "Не указано"
    end = format_datetime(event["end"].replace("+03:00", "")) if "end" in event else "Не указано"
    color = event.get("color", event.get("backgroundColor", "#FF6C6C"))
    description = event.get("extendedProps", {}).get("description", event.get("description", "Описание отсутствует"))

    st.markdown(
        f"""
        #### <span style='color:{color};'>⬤</span> {title}  
        **Начало:** {start}  
        **Конец:** {end}  
        **Описание:** {description}  
        """, 
        unsafe_allow_html=True
    )
    
    if st.button("Редактировать мероприятие"):
        st.session_state["editing_event"] = event
    
    if "editing_event" in st.session_state and st.session_state["editing_event"] == event:
        edit_event_form(event)
        
        username = st.session_state["username"]
        event_details = find_event_by_details(username, event["title"], event["start"], event["end"])
        if event_details:
            if st.button("Удалить мероприятие"):
                if delete_event(event_details["id"], username):
                    st.success("Мероприятие удалено!")
                    del st.session_state["editing_event"]
                    st.rerun()
                else:
                    st.error("Ошибка удаления мероприятия!")
        else:
            st.error("Мероприятие не найдено в базе данных!")


def render_calendar(events: list):
    """Отрисовка календаря и обработка взаимодействий"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        calendar_events = calendar(events=events, options=CALENDAR_CONFIG)
    
    with col2:
        if calendar_events:
            callback_type = calendar_events.get("callback")
            if callback_type == "dateClick":
                if "editing_event" in st.session_state:
                    del st.session_state["editing_event"]
                display_date_selection(calendar_events["dateClick"]["date"])
            elif callback_type == "eventClick":
                clicked_event = calendar_events["eventClick"]["event"]
                if "selected_date" in st.session_state:
                    del st.session_state["selected_date"]
                if "editing_event" in st.session_state and st.session_state["editing_event"] != clicked_event:
                    del st.session_state["editing_event"]
                display_event_details(clicked_event)


def main():
    """Основная логика приложения"""
    if not setup_page():
        return
    
    username = st.session_state["username"]
    events = get_user_events_for_render_calendar(username)
    render_calendar(events)
    st.page_link("app.py", label="Вернуться на главную", icon="🏠")


if __name__ == "__main__":
    main()