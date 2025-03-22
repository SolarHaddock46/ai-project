import streamlit as st
from ui.sidebar import render_sidebar
from ui.dashboard import display_dashboard
from ui.welcome import display_welcome_message
from chat.chat_utils import load_chat_history
from chat.llm_integration import load_hf_llm
from dotenv import load_dotenv

load_dotenv()

def initialize_session():
    """Инициализация состояния сессии."""
    if "chat_history" not in st.session_state:
        username = st.session_state.get("username")
        st.session_state.chat_history = (
            load_chat_history(username) if username else []
        )
    if "llm" not in st.session_state:
        st.session_state.llm = load_hf_llm()

def main():
    """Основная функция приложения."""
    st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="collapsed")
    render_sidebar()
    initialize_session()

    if st.session_state.get("username"):
        display_dashboard()
    else:
        display_welcome_message()

if __name__ == "__main__":
    main()