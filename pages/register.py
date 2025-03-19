import streamlit as st
from database.database import register_user
from hash.hash import hash_password
from ui.sidebar import render_sidebar

# Устанавливаем конфигурацию страницы в самом начале
st.set_page_config(page_title="Регистрация", layout="wide", initial_sidebar_state="collapsed")

# Отрисовка боковой панели
render_sidebar()

# Основной контент
st.title("📝 Регистрация")

if not st.session_state.get("username"):
    username = st.text_input("Введите имя пользователя")
    password = st.text_input("Введите пароль", type="password")
    confirm_password = st.text_input("Повторите пароль", type="password")

    if st.button("Зарегистрироваться"):
        if password != confirm_password:
            st.error("Пароли не совпадают!")
        elif register_user(username, password):
            st.success("✅ Регистрация успешна!")
            st.page_link("app.py", label="Перейти на главную")
        else:
            st.error("Ошибка! Такой пользователь уже существует.")
else:
    st.write("Вы уже авторизованы. Перейдите на главную страницу.")
    st.page_link("app.py", label="Перейти на главную")