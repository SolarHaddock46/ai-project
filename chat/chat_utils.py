import os
import json
import time
import logging
import base64
from typing import Optional, List, Dict
from dotenv import load_dotenv
from gtts import gTTS
import streamlit as st
from streamlit_chat import message
from chat.rag_processor import RAGProcessor
from chat.agent_processor import AgentProcessor
from langchain.memory import ConversationBufferMemory
from huggingface_hub import InferenceClient

load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
CHAT_HISTORY_DIR = "chat/history"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация процессоров
memory = ConversationBufferMemory()
rag_processor = None
agent_processor = None

client = None
if HUGGINGFACE_TOKEN:
    try:
        client = InferenceClient(token=HUGGINGFACE_TOKEN)
    except Exception as e:
        logger.error(f"Ошибка инициализации клиента Hugging Face: {e}")

def initialize_processors():
    """Инициализирует процессоры, если они ещё не созданы."""
    global rag_processor, agent_processor
    if rag_processor is None:
        if "llm" not in st.session_state:
            raise ValueError("Модель LLM не инициализирована в st.session_state. Убедитесь, что она задаётся в app.py или другом месте перед использованием процессоров.")
        rag_processor = RAGProcessor(st.session_state.llm)
    if agent_processor is None:
        agent_processor = AgentProcessor()

def load_chat_history(username: str) -> List[Dict]:
    """Загружает историю чата для пользователя."""
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    history_file = os.path.join(CHAT_HISTORY_DIR, f"{username}_chat_history.json")
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        return [msg for msg in history if time.time() - msg["timestamp"] <= 86400]
    return []

def save_chat_history(username: str, history: List[Dict]) -> None:
    """Сохраняет историю чата."""
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    history_file = os.path.join(CHAT_HISTORY_DIR, f"{username}_chat_history.json")
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False)

def clear_chat_history(username: str) -> None:
    """Очищает историю чата."""
    history_file = os.path.join(CHAT_HISTORY_DIR, f"{username}_chat_history.json")
    if os.path.exists(history_file):
        os.remove(history_file)
    st.session_state.chat_history = []

def text_to_speech(text: str) -> Optional[str]:
    """Преобразует текст в аудио."""
    try:
        tts = gTTS(text=text, lang="ru")
        temp_file = f"chat/temp_bot_audio_{int(time.time())}.mp3"
        tts.save(temp_file)
        with open(temp_file, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")
        os.remove(temp_file)
        return audio_data
    except Exception as e:
        logger.error(f"Ошибка преобразования текста в речь: {e}")
        return None

def recognize_speech(audio_path: str) -> str:
    """Распознает речь из аудиофайла."""
    if not client:
        return "Ошибка: клиент распознавания не инициализирован"
    try:
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        result = client.automatic_speech_recognition(audio_data)
        return result.get("text", str(result))
    except Exception as e:
        logger.error(f"Ошибка распознавания речи: {e}")
        return f"Ошибка сервиса распознавания: {e}"

def process_user_input(user_input: Optional[str] = None, audio_data: Optional[str] = None) -> None:
    """Обрабатывает пользовательский ввод."""
    username = st.session_state.get("username")
    if not username:
        return

    initialize_processors()

    history = st.session_state.chat_history
    current_time = time.time()

    if user_input:
        message = {"is_user": True, "type": "text", "content": user_input, "timestamp": current_time}
        history.append(message)
        response_text = generate_bot_response(user_input, is_audio=False)
        bot_response = {
            "is_user": False,
            "type": "text",
            "content": response_text,
            "timestamp": current_time
        }
        history.append(bot_response)
    elif audio_data:
        temp_dir = "chat/stt_temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        temp_audio_path = os.path.join(temp_dir, f"temp_audio_{len(history)}.wav")
        audio_bytes = base64.b64decode(audio_data)
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)

        recognized_text = recognize_speech(temp_audio_path)
        try:
            os.remove(temp_audio_path)
        except Exception as e:
            logger.error(f"Ошибка удаления временного файла: {e}")

        message = {
            "is_user": True,
            "type": "audio",
            "content": audio_data,
            "text": recognized_text,
            "timestamp": current_time
        }
        history.append(message)
        response_text = generate_bot_response(recognized_text, is_audio=True)
        audio_content = text_to_speech(response_text)
        bot_response = {
            "is_user": False,
            "type": "audio" if audio_content else "text",
            "content": audio_content or response_text,
            "text": response_text if audio_content else None,
            "timestamp": current_time
        }
        history.append(bot_response)

    st.session_state.chat_history = [msg for msg in history if time.time() - msg["timestamp"] <= 86400]
    save_chat_history(username, st.session_state.chat_history)
    st.rerun()

def display_chat() -> None:
    """Отображает историю чата."""
    with st.container(height=300):
        for i, msg in enumerate(st.session_state.chat_history):
            if msg["type"] == "text":
                message(msg["content"], is_user=msg["is_user"], key=f"msg_{i}")
            elif msg["type"] == "audio":
                audio_bytes = base64.b64decode(msg["content"])
                st.audio(audio_bytes, format="audio/mp3" if not msg["is_user"] else "audio/wav")
                text_content = msg.get("text", "(Аудиосообщение не распознано)")
                message(text_content, is_user=msg["is_user"], key=f"msg_{i}")

def generate_bot_response(user_input: str,is_audio: bool) -> str:
    """Обрабатывает запросы с учётом неопределённости."""
    # Проверка на неопределённость
    if _is_vague_query(user_input):
        # Сохраняем контекст для последующих уточнений
        clarification = _generate_clarification_question(user_input)
        memory.save_context({"input": user_input}, {"output": ""})
        return clarification

    # Проверка на уточняющий ответ
    elif memory.load_memory_variables({})["history"]:
        history = memory.load_memory_variables({})["history"]
        full_query = f"{history}\nУточнение: {user_input}"
        memory.clear()
        return _process_standard_query(full_query)
    else:
        return _process_standard_query(user_input)

def _process_standard_query(query: str) -> str:
    """Стандартная обработка (RAG/агенты)."""
    initialize_processors()
    if _is_simple_query(query):
        return rag_processor.process_query(query)
    return agent_processor.process_query(query)

def _is_simple_query(query: str) -> bool:
    """Определяет, является ли запрос простым (информационным)."""
    keywords = ["какие", "когда", "сколько", "покажи", "найди"]
    action_keywords = ["добавить", "установить", "изменить", "удалить"]
    return any(keyword in query.lower() for keyword in keywords) and not any(keyword in query.lower() for keyword in action_keywords)

def _is_vague_query(query: str) -> bool:
    """Определяет, является ли запрос неопределённым."""
    vague_keywords = [
        "кое-что", "что-нибудь", "напомни",
        "важное", "срочное", "похожее", "добавь задачу", "удали задачу"
    ]
    return any(keyword in query.lower() for keyword in vague_keywords) and len(query.split()) < 5

def _generate_clarification_question(query: str) -> str:
    """Генерирует уточняющий вопрос на основе типа запроса."""
    if "добавь задачу" in query.lower():
        return "Какую задачу добавить? Укажите название и дату."
    elif "удали задачу" in query.lower():
        return "Какую задачу удалить? Укажите ID или название."
    elif "покажи задачи" in query.lower():
        return "На какой период показать задачи? Например, 'на сегодня' или 'на неделю'."
    return "Пожалуйста, уточните ваш запрос."
