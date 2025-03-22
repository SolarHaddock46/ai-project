# import os
# import requests
# import logging
# from langchain_community.llms import HuggingFaceEndpoint
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# def load_hf_llm():
#     api_key = os.getenv("HUGGINGFACE_TOKEN")
#     if not api_key:
#         logger.error("HUGGINGFACE_TOKEN не найден в переменных окружения.")
#         raise ValueError("HUGGINGFACE_TOKEN не задан в .env")
#     try:
#         llm = HuggingFaceEndpoint(
#             endpoint_url="https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-alpha",
#             huggingfacehub_api_token=api_key,  # Авторизация через токен
#             max_length=512,
#             temperature=0.7
#         )
#         # Тестовый вызов для проверки авторизации
#         test_response = llm("Тестовый запрос для проверки API")
#         logger.info(f"Модель успешно инициализирована. Тестовый ответ: {test_response}")
#         return llm
#     except Exception as e:
#         logger.error(f"Ошибка инициализации модели: {e}")
#         raise ValueError(f"Не удалось инициализировать модель: {e}")
#
# class HuggingFaceAPI:
#     def __init__(self):
#         self.api_key = os.getenv("HUGGINGFACE_TOKEN")
#         if not self.api_key:
#             raise ValueError("HUGGINGFACE_TOKEN не задан в .env")
#
#     def generate_text(self, prompt: str) -> str:
#         llm = load_hf_llm()
#         return llm(prompt)


import os
import logging
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_hf_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY не найден в переменных окружения.")
        raise ValueError("GROQ_API_KEY не задан")
    try:
        llm = ChatGroq(
            temperature=0.7,
            model_name="gemma2-9b-it",
            groq_api_key=api_key,
            max_tokens=512
        )
        # Тестовый вызов
        test_response = llm.invoke([HumanMessage(content="Тестовый запрос для проверки API")]).content
        logger.info(f"Модель успешно инициализирована. Тестовый ответ: {test_response}")
        return llm
    except Exception as e:
        logger.error(f"Ошибка инициализации модели: {e}", exc_info=True)
        raise ValueError(f"Не удалось инициализировать модель: {e}")

class GroqAPI:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY не задан в .env")

    def generate_text(self, prompt: str) -> str:
        llm = load_hf_llm()
        try:
            return llm.invoke([HumanMessage(content=prompt)]).content
        except Exception as e:
            logger.error(f"Ошибка генерации текста: {e}", exc_info=True)
            raise RuntimeError(f"Ошибка при выполнении запроса: {e}")





# import os
# from huggingface_hub import InferenceClient
# from dotenv import load_dotenv
# from .inference_client_llm import InferenceClientLLM
#
# load_dotenv()
# HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
#
# def load_hf_llm():
#     """Загружает модель через InferenceClient, обёрнутую в LLM."""
#     if not HUGGINGFACE_TOKEN:
#         raise ValueError("HUGGINGFACE_TOKEN не задан в .env")
#
#     client = InferenceClient(token=HUGGINGFACE_TOKEN)
#     model = "HuggingFaceH4/zephyr-7b-alpha"
#     return InferenceClientLLM(client=client, model=model, max_length=512, temperature=0.7)
#
# class HuggingFaceAPI:
#     def __init__(self):
#         self.client = InferenceClient(token=HUGGINGFACE_TOKEN)
#
#     def generate_text(self, prompt: str) -> str:
#         return self.client.text_generation(
#             prompt,
#             max_new_tokens=512,
#             temperature=0.7,
#             stop=["\n"]  # Исправлено с stop_sequences
#         )