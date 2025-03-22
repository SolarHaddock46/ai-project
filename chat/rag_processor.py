from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import FAISS
from chat.llm_tools import EventTools
from database.database import get_events_by_day, get_events_by_week, get_events_by_month, get_user_events_for_change
from datetime import datetime, timedelta
import os
import streamlit as st

class RAGProcessor:
    def __init__(self, llm):
        self.api_key = os.getenv("HUGGINGFACE_TOKEN")
        self.embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=self.api_key,
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        self.llm = llm
        self.vector_store = None

    def update_vector_store(self) -> None:
        """Обновляет векторное хранилище данными из базы мероприятий."""
        events_text = EventTools.get_events()
        self.vector_store = FAISS.from_texts([events_text], self.embeddings)

    def _build_context_prompt(self, query: str) -> str:
        """Добавляет подсказки о форматах дат в запрос."""
        return f"""
            Вопрос: {query}

            Контекст:
            1. Относительные даты: 
               - "завтра 14:00", "через 3 дня", "следующая пятница в 11:30".
            2. Абсолютные даты: 
               - "15.04.2024 14:00", "2024-04-20T09:00".
            3. Если время не указано, используется 09:00.

            Примеры:
            - "Добавь встречу через 2 дня в 15:30" → дата: {EventTools._parse_datetime("через 2 дня 15:30")}
            - "Перенеси задачу на следующую среду" → дата: {EventTools._parse_datetime("следующая среда 09:00")}
        """

    def process_query(self, query: str) -> str:
        """Обрабатывает запрос с учётом контекста дат и фильтрации задач."""
        self.update_vector_store()
        username = st.session_state.get("username", "")

        # Обработка запросов на просмотр задач
        print(query.lower())
        if "на сегодня" in query.lower():
            today = datetime.now().strftime("%Y-%m-%d")
            events = get_events_by_day(username, today)
            return "📅 **Задачи на сегодня:**\n" + "\n".join(
                [f"- {e['title']} ({datetime.fromisoformat(e['start']).strftime('%H:%M')})"
                 for e in events]
            ) or "Задач нет."
        elif "на завтра" in query.lower():
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            events = get_events_by_day(username, tomorrow)
            return "📅 **Задачи на завтра:**\n" + "\n".join(
                [f"- {e['title']} ({datetime.fromisoformat(e['start']).strftime('%H:%M')})"
                 for e in events]
            ) or "Задач нет."
        elif "на неделю" in query.lower():
            start_of_week = datetime.now().replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d")
            events = get_events_by_week(username, start_of_week)
            return "📅 **Задачи на неделю:**\n" + "\n".join(
                [f"- {e['title']} ({datetime.fromisoformat(e['start']).strftime('%H:%M')})"
                 for e in events]
            ) or "Задач нет."
        elif "на месяц" in query.lower():
            now = datetime.now()
            events = get_events_by_month(username, now.month, now.year)
            return "📅 **Задачи на месяц:**\n" + "\n".join(
                [f"- {e['title']} ({datetime.fromisoformat(e['start']).strftime('%H:%M')})"
                 for e in events]
            ) or "Задач нет."
        elif "все задачи" in query.lower():
            events = get_user_events_for_change(username)
            return "📅 **Все задачи:**\n" + "\n".join(
                [f"- {e['title']} ({datetime.fromisoformat(e['start']).strftime('%Y-%m-%d %H:%M')})"
                 for e in events]
            ) or "Задач нет."
        else:
            events = get_user_events_for_change(username)
            return "📅 **Все задачи:**\n" + "\n".join(
                [f"- {e['title']} ({datetime.fromisoformat(e['start']).strftime('%Y-%m-%d %H:%M')})"
                 for e in events]
            ) or "Задач нет."

        # Обычная обработка через RAG
        augmented_query = self._build_context_prompt(query)
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 2}),
            return_source_documents=True
        )
        result = qa_chain({"query": augmented_query})
        return result["result"]
