# from langchain.agents import AgentType, initialize_agent
# from langchain.tools import Tool
# from langchain.memory import ConversationBufferMemory
# from chat.llm_integration import load_hf_llm
# from database.database import update_event, find_event_by_details
# import streamlit as st
# from chat.llm_tools import EventTools
#
# class AgentProcessor:
#     def __init__(self):
#         self.memory = ConversationBufferMemory(memory_key="chat_history")
#         self.llm = load_hf_llm()
#         self.tools = [
#             Tool(
#                 name="update_event_title",
#                 func=self._update_event_title_wrapper,
#                 description="Изменить заголовок мероприятия. Аргументы: event_id, new_title."
#             ),
#             Tool(
#                 name="update_event_description",
#                 func=self._update_event_description_wrapper,
#                 description="Изменить описание мероприятия. Аргументы: event_id, new_description."
#             ),
#             Tool(
#                 name="update_event_color",
#                 func=self._update_event_color_wrapper,
#                 description="Изменить цвет мероприятия. Аргументы: event_id, new_color."
#             ),
#             Tool(
#                 name="update_event",
#                 func=self._update_event_wrapper,
#                 description="Изменить дату мероприятия. Аргументы: old_title, new_start, new_end."
#             ),
#             Tool(
#                 name="add_event",
#                 func=self._add_event_wrapper,
#                 description="Добавить новое мероприятие. Формат: Название (в кавычках), Дата начала (в кавычках), Дата окончания (в кавычках). Пример: add_event(\"Встреча\", \"2024-06-15 14:00\", \"2024-06-15 15:00\")"
#             ),
#             Tool(
#                 name="delete_event",
#                 func=self._delete_event_wrapper,
#                 description="Удалить мероприятие. Аргументы: event_title."
#             )
#         ]
#
#         self.agent = initialize_agent(
#             tools=self.tools,
#             llm=self.llm,
#             agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
#             memory=self.memory,
#             verbose=True,
#             input_variables=["input"],
#             handle_parsing_errors=True
#         )
#
#     def _update_event_title_wrapper(self, args: str) -> str:
#         try:
#             event_id, new_title = [arg.strip() for arg in args.split(",", 1)]
#             username = "current_user"  # Предполагается, что username доступен через сессию
#             update_event(event_id, username, title=new_title)
#             return f"Заголовок мероприятия {event_id} изменён на '{new_title}'."
#         except Exception as e:
#             return f"Ошибка: {e}"
#
#     def _update_event_description_wrapper(self, args: str) -> str:
#         try:
#             event_id, new_description = [arg.strip() for arg in args.split(",", 1)]
#             username = "current_user"
#             update_event(event_id, username, description=new_description)
#             return f"Описание мероприятия {event_id} изменено на '{new_description}'."
#         except Exception as e:
#             return f"Ошибка: {e}"
#
#     def _update_event_color_wrapper(self, args: str) -> str:
#         try:
#             event_id, new_color = [arg.strip() for arg in args.split(",", 1)]
#             username = "current_user"
#             update_event(event_id, username, color=new_color)
#             return f"Цвет мероприятия {event_id} изменён на '{new_color}'."
#         except Exception as e:
#             return f"Ошибка: {e}"
#
#     def _update_event_wrapper(self, args: str) -> str:
#         try:
#             old_title, new_start, new_end = [arg.strip() for arg in args.split(",")]
#             username = st.session_state.get("username", "")
#             update_event(old_title, username, start=new_start, end=new_end)
#             return f"Мероприятие '{old_title}' перенесено на {new_start} - {new_end}."
#         except ValueError:
#             return "Некорректные аргументы. Ожидается: old_title, new_start, new_end."
#         except Exception as e:
#             return f"Ошибка обновления мероприятия: {e}"
#
#     def process_query(self, query: str) -> str:
#         """Обрабатывает сложные запросы через агента."""
#         inputs = {"input": query}
#         try:
#             response = self.agent.invoke(inputs)
#             print("response: ", response)
#             return response.get("output", "Не удалось обработать запрос")
#         except ValueError as e:
#             if "output parsing error" in str(e):
#                 return "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте переформулировать вопрос."
#             else:
#                 raise e
#
#     def _add_event_wrapper(self, args: str) -> str:
#         try:
#             args_list = [arg.strip('"') for arg in args.split(",", 2)]
#             if len(args_list) != 3:
#                 return "Ошибка: Неверный формат. Требуется: Название, Начало, Конец."
#             title, start, end = args_list
#             username = st.session_state.get("username", "")
#             if not username:
#                 return "Ошибка: Пользователь не авторизован."
#             result = EventTools.add_event(title, start, end)
#             return result["message"]
#         except Exception as e:
#             return f"Ошибка: {str(e)}"
#
#     def _delete_event_wrapper(self, args: str) -> str:
#         try:
#             event_title = args.strip('"')
#             username = st.session_state.get("username", "")
#             if not event_title:
#                 return "Ошибка: Укажите название задачи в кавычках."
#             result = EventTools.delete_event(event_title)
#             return result["message"]
#         except Exception as e:
#             return f"Ошибка: {str(e)}"


from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import ConversationalChatAgent
from chat.llm_integration import load_hf_llm
from database.database import update_event, find_event_by_details
from chat.llm_tools import EventTools
import streamlit as st
from chat.llm_tools import EventTools
import shlex
import json


class AgentProcessor:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.llm = load_hf_llm()

        # Кастомизированный системный промпт
#         self.system_prompt = """Ты - интеллектуальный помощник по работе с календарем. Всегда придерживайся следующих правил:
# 1. Все даты должны быть в формате YYYY-MM-DD HH:mm
# 2. Названия событий заключай в двойные кавычки
# 3. Всегда проверяй наличие необходимых аргументов
# 4. Если нужно уточнить детали - задавай вопросы
# 5. Для идентификации событий используй точные названия
# 6. Формат ответов строго по шаблону:
#
# Пример:
# Пользователь: "Перенеси встречу на завтра в 15:00"
# Ты должен:
# Thought: Нужно найти ID встречи и обновить даты
# Action: find_event_by_details
# Action Input: {"title": "встреча"}
# Observation: Найдено событие ID:123
# Action: update_event
# Action Input: {"event_id": "123", "new_start": "2024-06-20 15:00", "new_end": "2024-06-20 16:00"}
# Final Answer: Событие успешно перенесено"""
        self.system_prompt = """Ты - интеллектуальный помощник по работе с календарем. ВСЕГДА:
        1. Используй ТОЛЬКО JSON-формат для Action Input
        2. Если получил ошибку JSON - исправь формат и повтори попытку
        3. Никогда не используй простые строки для аргументов
        4. Все строковые значения заключай в двойные кавычки

        Пример правильного формата:
        Action: add_event
        Action Input: {"title": "Совещание", "start": "2024-06-20 14:00", "end": "2024-06-20 15:00"}"""

        self.tools = [
            Tool(
                name="update_event_title",
                func=self._update_event_title_wrapper,
                description=(
                    "ИЗМЕНИТЬ ЗАГОЛОВОК. Формат: "
                    "'event_id' (строка), 'new_title' (строка в кавычках). "
                    "Пример: update_event_title(\"event_123\", \"Новое название\")"
                )
            ),
            Tool(
                name="update_event_description",
                func=self._update_event_description_wrapper,
                description=(
                    "ИЗМЕНИТЬ ОПИСАНИЕ. Формат: "
                    "'event_id' (строка), 'new_description' (строка в кавычках). "
                    "Пример: update_event_description(\"event_123\", \"Новое описание...\")"
                )
            ),
            Tool(
                name="update_event_color",
                func=self._update_event_color_wrapper,
                description=(
                    "ИЗМЕНИТЬ ЦВЕТ. Формат: "
                    "'event_id' (строка), 'new_color' (HEX-код цвета). "
                    "Пример: update_event_color(\"event_123\", \"#FF0000\")"
                )
            ),
            Tool(
                name="update_event",
                func=self._update_event_wrapper,
                description=(
                    "ИЗМЕНИТЬ ДАТУ СОБЫТИЯ. Формат: "
                    "'event_id' (строка), 'new_start' (дата), 'new_end' (дата). "
                    "Пример: update_event(\"event_123\", \"2024-06-20 14:00\", \"2024-06-20 15:00\")"
                )
            ),
            Tool(
                name="add_event",
                func=self._add_event_wrapper,
                description=(
                    "ДОБАВИТЬ СОБЫТИЕ. Формат: "
                    "'title' (строка в кавычках), 'start' (дата), 'end' (дата). "
                    "Пример: add_event(\"Совещание\", \"2024-06-18 14:00\", \"2024-06-18 15:00\")"
                )
            ),
            Tool(
                name="delete_event",
                func=self._delete_event_wrapper,
                description=(
                    "УДАЛИТЬ СОБЫТИЕ. Формат: "
                    "'event_title' (точное название в кавычках). "
                    "Пример: delete_event(\"Важная встреча\")"
                )
            ),
            Tool(
                name="find_event_by_details",
                func=self._find_event_wrapper,
                description=(
                    "ПОИСК СОБЫТИЙ. Формат: "
                    "'title' (часть названия в кавычках), 'date' (опционально, дата). "
                    "Пример: find_event_by_details(\"встреча\", \"2024-06-18\")"
                )
            )
        ]

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            agent_kwargs={
                'system_message': self.system_prompt,
                'input_variables': ['input', 'chat_history', 'agent_scratchpad']
            },
            handle_parsing_errors="Проверь формат аргументов и повтори запрос",
            max_iterations=6,
            early_stopping_method="force",
            max_execution_time=30
        )

    def _find_event_wrapper(self, args: str) -> str:
        try:
            args_dict = json.loads(args)
            title = args_dict.get('title', '')
            date = args_dict.get('date', None)
            events = find_event_by_details(title, date)
            return json.dumps({'status': 'success', 'events': events})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

    # def _update_event_title_wrapper(self, args: str) -> str:
    #     try:
    #         new_title = args
    #         username = st.session_state.get("username", "")
    #         update_event(username, title=new_title)
    #         return json.dumps({'status': 'success'})
    #     except Exception as e:
    #         return json.dumps({'status': 'error', 'message': str(e)})

    def _update_event_title_wrapper(self, args: str) -> str:
        try:
            parts = args.split('", "')
            old_title = parts[0].strip('"')
            new_title = parts[1].strip('"')
            username = st.session_state.get("username", "")
            success = update_event(username, title=old_title, **{'new_title': new_title})
            return json.dumps({'status': 'success' if success else 'error'})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

    def _update_event_description_wrapper(self, args: str) -> str:
        try:
            parts = args.split('", "')
            title = parts[0].strip('"')
            new_description = parts[1].strip('"')
            username = st.session_state.get("username", "")
            success = update_event(username, title=title, **{'description': new_description})
            return json.dumps({'status': 'success' if success else 'error', 'event_id': title})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

    def _update_event_color_wrapper(self, args: str) -> str:
        try:
            parts = args.split('", "')
            title = parts[0].strip('"')
            new_color = parts[1].strip('"')
            username = st.session_state.get("username", "")
            success = update_event(username, title=title, **{'color': new_color})
            return json.dumps({'status': 'success' if success else 'error', 'event_id': title})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

    def _update_event_wrapper(self, args: str) -> str:
        try:
            parts = args.split('", "')
            title = parts[0].strip('"')
            new_start = parts[1].strip('"')
            new_end = parts[2].strip('"')
            new_start_iso = EventTools._parse_datetime(new_start)
            new_end_iso = EventTools._parse_datetime(new_end)
            username = st.session_state.get("username", "")
            success = update_event(username, title=title, **{'start': new_start_iso, 'end': new_end_iso})
            return json.dumps({'status': 'success' if success else 'error', 'event_id': title})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

    # def _update_event_description_wrapper(self, args: str) -> str:
    #     try:
    #         args_dict = json.loads(args)
    #         event_id = args_dict['event_id']
    #         new_description = args_dict['new_description']
    #         username = st.session_state.get("username", "")
    #         update_event(event_id, username, description=new_description)
    #         return json.dumps({'status': 'success', 'event_id': event_id})
    #     except Exception as e:
    #         return json.dumps({'status': 'error', 'message': str(e)})
    #
    # def _update_event_color_wrapper(self, args: str) -> str:
    #     try:
    #         args_dict = json.loads(args)
    #         event_id = args_dict['event_id']
    #         new_color = args_dict['new_color']
    #         username = st.session_state.get("username", "")
    #         update_event(event_id, username, color=new_color)
    #         return json.dumps({'status': 'success', 'event_id': event_id})
    #     except Exception as e:
    #         return json.dumps({'status': 'error', 'message': str(e)})
    #
    # def _update_event_wrapper(self, args: str) -> str:
    #     try:
    #         args_dict = json.loads(args)
    #         event_id = args_dict['event_id']
    #         new_start = args_dict['new_start']
    #         new_end = args_dict['new_end']
    #         username = st.session_state.get("username", "")
    #         update_event(event_id, username, start=new_start, end=new_end)
    #         return json.dumps({'status': 'success', 'event_id': event_id})
    #     except Exception as e:
    #         return json.dumps({'status': 'error', 'message': str(e)})

    # def _add_event_wrapper(self, args: str) -> str:
    #     try:
    #         args_dict = json.loads(args)
    #         title = args_dict['title']
    #         start = args_dict['start']
    #         end = args_dict['end']
    #         username = st.session_state.get("username", "")
    #         result = EventTools.add_event(title, start, end)
    #         return json.dumps({'status': 'success', 'event_id': result['event_id']})
    #     except Exception as e:
    #         return json.dumps({'status': 'error', 'message': str(e)})

    def _add_event_wrapper(self, args: str) -> str:
        """Обработка добавления событий с улучшенным парсингом"""
        try:
            # Автоматическое исправление формата
            try:
                args_dict = json.loads(args)
            except json.JSONDecodeError:
                # Попытка восстановить формат из строки
                parts = [p.strip(' "\'') for p in args.split(",")]
                if len(parts) == 3:
                    args_dict = {
                        "title": parts[0],
                        "start": parts[1],
                        "end": parts[2]
                    }
                else:
                    raise ValueError("Некорректный формат аргументов")

            # Валидация обязательных полей
            required_fields = ['title', 'start', 'end']
            for field in required_fields:
                if field not in args_dict:
                    raise ValueError(f"Отсутствует обязательное поле: {field}")

            # Вызов логики добавления
            username = st.session_state.get("username", "")
            result = EventTools.add_event(
                title=args_dict['title'],
                start=args_dict['start'],
                end=args_dict['end']
            )

            return json.dumps({
                "status": "success",
                "event_id": result.get("event_id"),
                "message": f"Событие '{args_dict['title']}' добавлено"
            })

        # except json.JSONDecodeError:
        #     return json.dumps({
        #         "status": "error",
        #         "message": f"Некорректный JSON формат. Пример: {{'title':'Событие','start':'2024-06-20 14:00','end':'2024-06-20 15:00'}}"
        #     })
        # except Exception as e:
        #     return json.dumps({"status": "error", "message": str(e)})

        except Exception as e:
            error_info = {
                "status": "error",
                "message": str(e),
                "correct_format": {
                    "title": "Название события",
                    "start": "ГГГГ-ММ-ДД ЧЧ:мм",
                    "end": "ГГГГ-ММ-ДД ЧЧ:мм"
                }
            }

    def _delete_event_wrapper(self, args: str) -> str:
        try:
            # print(args)
            # args_dict = json.loads(args)
            # print(args_dict)
            # event_title = args_dict['event_title']
            event_title = args
            username = st.session_state.get("username", "")
            result = EventTools.delete_event(event_title)
            return json.dumps({'status': 'success', 'deleted_title': event_title})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})

    # def process_query(self, query: str) -> str:
    #     """Обработка запроса с автоматическим исправлением формата"""
    #     try:
    #         # Автоматическое исправление кавычек
    #         query = query.replace("'", '"')
    #
    #         print(f"\n[ВХОДНОЙ ЗАПРОС]: {query}")
    #         response = self.agent.invoke({"input": query})
    #         print(f"[ОТВЕТ АГЕНТА]: {response}")
    #         return response.get("output", "Не удалось обработать запрос")
    #     except Exception as e:
    #         print(f"[ОШИБКА]: {str(e)}")
    #         return "Произошла ошибка обработки. Пожалуйста, уточните запрос."

    def process_query(self, query: str) -> str:
        """Обработка запроса с повторными попытками"""
        try:
            print(f"\n[Запрос]: {query}")
            response = self.agent.invoke(
                {"input": query},
                {"max_retries": 2}  # Добавляем повторные попытки
            )

            # Если в ответе есть указание на ошибку JSON - повторяем
            if "JSON" in response.get("output", "") and "ошибка" in response.get("output", "").lower():
                print("Обнаружена ошибка JSON, повторная обработка...")
                return self.agent.invoke({"input": "Исправь JSON формат для предыдущего запроса"})

            return response.get("output", "Не удалось обработать запрос")

        except Exception as e:
            return f"Критическая ошибка: {str(e)}"




# from langchain.prompts import PromptTemplate
# from langchain_core.output_parsers import JsonOutputParser
# from langchain_core.runnables import RunnablePassthrough
# from pydantic import BaseModel, Field, ValidationError, validator
# from typing import Literal, Optional
# from datetime import datetime, timedelta
# from database.database import add_event, delete_event_by_title, update_event
# import streamlit as st
# import logging
# import dateparser
#
# logger = logging.getLogger(__name__)
#
#
# # Модель валидации запросов
# class TaskSchema(BaseModel):
#     action: Literal["add", "delete", "update"] = Field(..., description="Тип операции")
#     title: str = Field(..., min_length=2, max_length=100, description="Название задачи")
#     start: Optional[str] = Field(None, pattern=r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", description="Дата начала")
#     end: Optional[str] = Field(None, pattern=r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", description="Дата окончания")
#     color: Optional[str] = Field(None, pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", description="HEX-цвет")
#
#     @validator("end", always=True)
#     def validate_dates(cls, v, values):
#         if values["action"] in ["add", "update"]:
#             start_str = values.get("start")
#             if not start_str:
#                 raise ValueError("Требуется поле start")
#
#             start = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
#             end = datetime.strptime(v, "%Y-%m-%d %H:%M") if v else start + timedelta(hours=1)
#
#             if end <= start:
#                 raise ValueError("Дата окончания должна быть позже начала")
#
#             return end.strftime("%Y-%m-%d %H:%M")
#         return v
#
#
# class AgentProcessor:
#     def __init__(self, llm):
#         self.llm = llm
#         self.parser = JsonOutputParser(pydantic_object=TaskSchema)
#         self.chain = self._build_chain()
#
#     def _build_chain(self):
#         prompt = PromptTemplate(
#             template="""Генерируй JSON строго по схеме:
#             {{
#                 "action": "add|delete|update",
#                 "title": "string",
#                 "start": "YYYY-MM-DD HH:MM",
#                 "end": "YYYY-MM-DD HH:MM",
#                 "color": "#HEX|undefined"
#             }}
#
#             Правила:
#             - Для действий add/update обязательны start и end
#             - Для delete требуется только title
#
#             Пример для add:
#             Запрос: {{"Добавь задачу 'Митинг' на завтра 14:00"}}
#             Ответ:
#             {{
#                 "action": "add",
#                 "title": "Митинг",
#                 "start": "{tomorrow_14}",
#                 "end": "{tomorrow_15}",
#                 "color": "#2196F3"
#             }}
#
#             Входной запрос: {{input}}
#             """.format(
#                 tomorrow_14=(datetime.now() + timedelta(days=1)).replace(hour=14, minute=0).strftime("%Y-%m-%d %H:%M"),
#                 tomorrow_15=(datetime.now() + timedelta(days=1)).replace(hour=15, minute=0).strftime("%Y-%m-%d %H:%M")
#             ),
#             input_variables=["input"]
#         )
#         return RunnablePassthrough() | prompt | self.llm | self.parser
#
#     def process_query(self, query: str) -> str:
#         try:
#             result = self.chain.invoke({"input": query})
#             return self._execute_action(result.dict())
#         except ValidationError as e:
#             error_msg = "\n".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
#             return f"❌ Ошибка формата:\n{error_msg}"
#         except Exception as e:
#             logger.exception("System error")
#             return f"⚠️ Внутренняя ошибка: {str(e)}"
#
#     def _execute_action(self, data: dict) -> str:
#         try:
#             username = st.session_state.get("username", "")
#             if not username:
#                 return "❌ Ошибка авторизации"
#
#             match data["action"]:
#                 case "add":
#                     return self._add_task(
#                         title=data["title"],
#                         start=data["start"],
#                         end=data["end"],
#                         color=data.get("color", "#4A90E2"),
#                         username=username
#                     )
#
#                 case "delete":
#                     return self._delete_task(
#                         title=data["title"],
#                         username=username
#                     )
#
#                 case "update":
#                     return self._update_task(
#                         title=data["title"],
#                         start=data["start"],
#                         end=data["end"],
#                         color=data.get("color"),
#                         username=username
#                     )
#
#         except KeyError as e:
#             return f"❌ Отсутствует поле: {str(e)}"
#         except ValueError as e:
#             return f"❌ Некорректные данные: {str(e)}"
#         except Exception as e:
#             logger.error(f"Action failed: {str(e)}")
#             return "⚠️ Ошибка выполнения операции"
#
#     def _add_task(self, title: str, start: str, end: str, color: str, username: str) -> str:
#         try:
#             add_event(
#                 username=username,
#                 title=title,
#                 start=self._parse_datetime(start),
#                 end=self._parse_datetime(end),
#                 color=color
#             )
#             return f"✅ Задача '{title}' добавлена"
#         except Exception as e:
#             return f"❌ Ошибка добавления: {str(e)}"
#
#     def _delete_task(self, title: str, username: str) -> str:
#         try:
#             if delete_event_by_title(username, title):
#                 return f"✅ Задача '{title}' удалена"
#             return f"⚠️ Задача '{title}' не найдена"
#         except Exception as e:
#             return f"❌ Ошибка удаления: {str(e)}"
#
#     def _update_task(self, title: str, start: str, end: str, color: str, username: str) -> str:
#         try:
#             if update_event(
#                     username=username,
#                     title=title,
#                     start=self._parse_datetime(start),
#                     end=self._parse_datetime(end),
#                     color=color
#             ):
#                 return f"✅ Задача '{title}' обновлена"
#             return f"⚠️ Задача '{title}' не найдена"
#         except Exception as e:
#             return f"❌ Ошибка обновления: {str(e)}"
#
#     def _parse_datetime(self, dt_str: str) -> str:
#         """Конвертация в ISO-формат с валидацией"""
#         try:
#             dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
#             return dt.isoformat()
#         except ValueError:
#             parsed = dateparser.parse(dt_str, languages=["ru"])
#             if not parsed:
#                 raise ValueError(f"Нераспознанный формат времени: {dt_str}")
#             return parsed.isoformat()