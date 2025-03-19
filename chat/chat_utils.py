import os
import json
import time
import logging
import base64
from typing import Optional, List, Dict
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from gtts import gTTS
import streamlit as st
from streamlit_chat import message

load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
CHAT_HISTORY_DIR = "chat/history"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = None
if HUGGINGFACE_TOKEN:
    try:
        client = InferenceClient(token=HUGGINGFACE_TOKEN)
    except Exception as e:
        logger.error(f"Ошибка инициализации клиента Hugging Face: {e}")

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

def process_user_input(user_input: Optional[str] = None, audio_data: Optional[str] = None) -> None:
    """Обрабатывает пользовательский ввод."""
    username = st.session_state.get("username")
    if not username:
        return

    history = st.session_state.chat_history
    current_time = time.time()

    if user_input:
        message = {"is_user": True, "type": "text", "content": user_input, "timestamp": current_time}
        history.append(message)
        bot_response = generate_bot_response(user_input, is_audio=False)
        bot_response["timestamp"] = current_time
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
        bot_response = generate_bot_response(recognized_text, is_audio=True)
        bot_response["timestamp"] = current_time
        history.append(bot_response)

    st.session_state.chat_history = [msg for msg in history if time.time() - msg["timestamp"] <= 86400]
    save_chat_history(username, st.session_state.chat_history)
    st.rerun()

def generate_bot_response(user_input: str, is_audio: bool = False) -> Dict:
    """Генерирует ответ бота."""
    user_input_lower = user_input.lower()
    if "мероприятие" in user_input_lower:
        response_text = "Какое мероприятие вы хотите запланировать?"
    elif "аудио" in user_input_lower:
        response_text = "Я получил ваше аудио!"
    else:
        response_text = "Я вас понял! Чем могу помочь?"

    if is_audio:
        audio_content = text_to_speech(response_text)
        return {
            "is_user": False,
            "type": "audio" if audio_content else "text",
            "content": audio_content or response_text,
            "text": response_text if audio_content else None
        }
    return {"is_user": False, "type": "text", "content": response_text}

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