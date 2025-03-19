import streamlit as st
import base64
from chat.chat_utils import process_user_input, display_chat

def display_dashboard():
    """Отображает дашборд для авторизованных пользователей."""
    st.title("📊 Дашборд мероприятий")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📅 Ближайшие мероприятия")
        st.info("🔹 Здесь будет информация о мероприятиях...")

        st.subheader("✅ Задачи по ближайшему мероприятию")
        st.warning("📌 Здесь будут задачи...")

    with col2:
        st.subheader("⛅ Погода")
        st.success("🌤 Виджет погоды...")

        st.subheader("💬 Чат с ИИ")
        display_chat()

        with st.form(key="chat_form", clear_on_submit=True):
            col_input, col_audio = st.columns([3, 1])
            with col_input:
                user_input = st.text_input("Введите сообщение", key="user_input")
            with col_audio:
                audio_input = st.audio_input("Записать голосовое", key="audio_input")
            submit_button = st.form_submit_button(label="Отправить")

            if submit_button:
                if user_input:
                    process_user_input(user_input=user_input)
                elif audio_input:
                    audio_data = base64.b64encode(audio_input.read()).decode("utf-8")
                    process_user_input(audio_data=audio_data)