import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from dotenv import load_dotenv
import os
from database.database import check_user
from hash.hash import hash_password
from chat.chat_utils import clear_chat_history

load_dotenv()
COOKIE_PASSWORD = os.getenv("COOKIE_PASSWORD")

def render_sidebar():
    """Отрисовка боковой панели."""
    cookies = EncryptedCookieManager(password=COOKIE_PASSWORD)
    if not cookies.ready():
        st.stop()

    if "username" not in st.session_state:
        st.session_state.username = None

    saved_username = cookies.get("username")
    saved_password_hash = cookies.get("password_hash")
    if saved_username and saved_password_hash and check_user(saved_username, saved_password_hash):
        st.session_state.username = saved_username

    st.sidebar.title("Ваш аккаунт")

    if not st.session_state.username:
        st.sidebar.subheader("🔐 Вход в аккаунт")
        username = st.sidebar.text_input("Имя пользователя")
        password = st.sidebar.text_input("Пароль", type="password")

        if st.sidebar.button("Войти"):
            if check_user(username, password):
                st.session_state.username = username
                cookies["username"] = username
                cookies["password_hash"] = hash_password(password)
                cookies.save()
                st.sidebar.success(f"Добро пожаловать, {username}!")
                st.rerun()
            else:
                st.sidebar.error("Неверное имя пользователя или пароль")

        st.sidebar.page_link("pages/register.py", label="Регистрация")
    else:
        st.sidebar.success(f"Вы вошли как {st.session_state.username}")
        if st.sidebar.button("Выйти"):
            username = st.session_state.username
            st.session_state.username = None
            cookies["username"] = ""
            cookies["password_hash"] = ""
            cookies.save()
            clear_chat_history(username)
            st.rerun()

        st.sidebar.subheader("📋 Меню")
        st.sidebar.page_link("app.py", label="Главная")
        st.sidebar.page_link("pages/calendar.py", label="Календарь")
        st.sidebar.page_link("pages/events_test.py", label="Тест мероприятий")