import streamlit as st
from ui.sidebar import render_sidebar
from database.database import add_event, update_event, delete_event, get_user_events_for_change
import datetime

# Настройка страницы
st.set_page_config(page_title="Тест мероприятий", layout="wide", initial_sidebar_state="collapsed")

def setup_page():
    """Настройка базовых элементов страницы."""
    render_sidebar()
    if not st.session_state.get("username"):
        st.warning("Пожалуйста, войдите в систему для доступа к странице.")
        st.page_link("app.py", label="Перейти к входу")
        return False
    st.title("📅 Управление мероприятиями")
    return True

def add_event_form():
    """Форма для добавления мероприятия."""
    st.subheader("Добавить мероприятие")
    with st.form(key="add_event_form"):
        title = st.text_input("Название мероприятия")
        start_date = st.date_input("Дата начала", value=datetime.date.today())
        start_time = st.time_input("Время начала", value=datetime.time(9, 0))
        end_date = st.date_input("Дата окончания", value=datetime.date.today())
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
            # Проверка, что start <= end
            start_dt = datetime.datetime.fromisoformat(start)
            end_dt = datetime.datetime.fromisoformat(end)
            if start_dt > end_dt:
                st.error("Дата и время окончания не могут быть раньше даты и времени начала. Пожалуйста, измените введённые данные.")
                return
            username = st.session_state["username"]
            add_event(username, title, start, end, color, description)
            st.success("Мероприятие добавлено!")
            st.rerun()

def edit_event_form(events):
    """Форма для редактирования мероприятия."""
    st.subheader("Редактировать мероприятие")
    event_options = {f"{e['title']} ({e['start']})": e["id"] for e in events}
    selected_event_id = st.selectbox("Выберите мероприятие", options=list(event_options.keys()))
    
    if selected_event_id:
        event_id = event_options[selected_event_id]
        event = next(e for e in events if e["id"] == event_id)
        
        with st.form(key="edit_event_form"):
            title = st.text_input("Название мероприятия", value=event["title"])
            start_dt = datetime.datetime.fromisoformat(event["start"])
            start_date = st.date_input("Дата начала", value=start_dt.date())
            start_time = st.time_input("Время начала", value=start_dt.time())
            end_dt = datetime.datetime.fromisoformat(event["end"])
            end_date = st.date_input("Дата окончания", value=end_dt.date())
            end_time = st.time_input("Время окончания", value=end_dt.time())
            color = st.color_picker("Цвет", value=event.get("color", "#FF6C6C"))
            description = st.text_area("Описание", value=event.get("description", ""))
            submit = st.form_submit_button("Сохранить изменения")

            if submit:
                if not title:
                    st.error("Название мероприятия обязательно!")
                    return
                start = f"{start_date}T{start_time}:00"
                end = f"{end_date}T{end_time}:00"
                # Проверка, что start <= end
                start_dt = datetime.datetime.fromisoformat(start)
                end_dt = datetime.datetime.fromisoformat(end)
                if start_dt > end_dt:
                    st.error("Дата и время окончания не могут быть раньше даты и времени начала. Пожалуйста, измените введённые данные.")
                    return
                username = st.session_state["username"]
                update_event(event_id, username, title, start, end, color, description)
                st.success("Мероприятие обновлено!")
                st.rerun()

def delete_event_form(events):
    """Форма для удаления мероприятия."""
    st.subheader("Удалить мероприятие")
    event_options = {f"{e['title']} ({e['start']})": e["id"] for e in events}
    selected_event_id = st.selectbox("Выберите мероприятие для удаления", options=list(event_options.keys()))
    
    if selected_event_id and st.button("Удалить"):
        event_id = event_options[selected_event_id]
        username = st.session_state["username"]
        if delete_event(event_id, username):
            st.success("Мероприятие удалено!")
            st.rerun()
        else:
            st.error("Ошибка удаления мероприятия!")

def main():
    """Основная логика страницы."""
    if not setup_page():
        return
    
    username = st.session_state["username"]
    events = get_user_events_for_change(username)
    # Формы управления мероприятиями
    col1, col2 = st.columns(2)
    with col1:
        add_event_form()
    with col2:
        edit_event_form(events)
        delete_event_form(events)
    
    st.page_link("app.py", label="Вернуться на главную", icon="🏠")

if __name__ == "__main__":
    main()