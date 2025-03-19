### На эту ошибку пофиг:
```st.cache` is deprecated and will be removed soon.```

```raise StreamlitSetPageConfigMustBeFirstCommandError()```

# Структура проекта

## app.py
Основной файл приложения, запускающий веб-интерфейс с помощью Streamlit.

- **Импорты:**
  - `streamlit as st` - Библиотека для создания веб-интерфейса.
  - `ui.sidebar.render_sidebar` - Функция отрисовки боковой панели.
  - `ui.dashboard.display_dashboard` - Функция отображения дашборда.
  - `ui.welcome.display_welcome_message` - Функция отображения приветственного сообщения.
  - `chat.chat_utils.load_chat_history` - Функция загрузки истории чата.

- **Функции:**
  - `initialize_session()` - Инициализирует состояние сессии, загружая историю чата для текущего пользователя, если он авторизован.
  - `main()` - Основная функция, настраивает конфигурацию страницы и управляет отображением: вызывает `render_sidebar()`, `initialize_session()`, а затем отображает либо дашборд, либо приветственное сообщение в зависимости от авторизации.

## ui/welcome.py
Модуль для отображения приветственного сообщения.

- **Импорты:**
  - `streamlit as st` - Библиотека для создания веб-интерфейса.

- **Функции:**
  - `display_welcome_message()` - Отображает заголовок "Добро пожаловать!" и сообщение с просьбой войти или зарегистрироваться.

## ui/sidebar.py
Модуль для управления боковой панелью с авторизацией и навигацией.

- **Импорты:**
  - `streamlit as st` - Библиотека для создания веб-интерфейса.
  - `streamlit_cookies_manager.EncryptedCookieManager` - Управление зашифрованными куки.
  - `dotenv.load_dotenv` - Загрузка переменных окружения из файла .env.
  - `os` - Работа с операционной системой.
  - `database.database.check_user` - Проверка существования пользователя.
  - `hash.hash.hash_password` - Хеширование пароля.
  - `chat.chat_utils.clear_chat_history` - Очистка истории чата.

- **Функции:**
  - `render_sidebar()` - Отрисовывает боковую панель: управляет авторизацией через куки, отображает форму входа или меню для авторизованного пользователя с кнопкой выхода и навигацией.

## ui/dashboard.py
Модуль для отображения дашборда авторизованных пользователей.

- **Импорты:**
  - `streamlit as st` - Библиотека для создания веб-интерфейса.
  - `base64` - Кодирование/декодирование данных.
  - `chat.chat_utils.process_user_input` - Обработка пользовательского ввода в чате.
  - `chat.chat_utils.display_chat` - Отображение чата.

- **Функции:**
  - `display_dashboard()` - Отображает дашборд с разделами: "Ближайшие мероприятия", "Задачи", "Погода" и "Чат с ИИ". Включает форму для текстового и аудиоввода в чат.

## pages/register.py
Страница регистрации новых пользователей.

- **Импорты:**
  - `streamlit as st` - Библиотека для создания веб-интерфейса.
  - `database.database.register_user` - Регистрация пользователя в базе данных.
  - `hash.hash.hash_password` - Хеширование пароля.
  - `ui.sidebar.render_sidebar` - Отрисовка боковой панели.

- **Основной код:**
  - Настраивает страницу и отображает форму регистрации с проверкой паролей. При успешной регистрации предлагает перейти на главную страницу.

## pages/events_test.py
Страница для тестирования управления мероприятиями.

- **Импорты:**
  - `streamlit as st` - Библиотека для создания веб-интерфейса.
  - `ui.sidebar.render_sidebar` - Отрисовка боковой панели.
  - `database.database.add_event`, `update_event`, `delete_event`, `get_user_events_for_change` - Функции работы с мероприятиями в базе данных.
  - `datetime` - Работа с датой и временем.

- **Функции:**
  - `setup_page()` - Настройка страницы, проверка авторизации.
  - `add_event_form()` - Форма добавления мероприятия с валидацией.
  - `edit_event_form(events)` - Форма редактирования выбранного мероприятия.
  - `delete_event_form(events)` - Форма удаления мероприятия.
  - `main()` - Основная логика страницы, отображает формы управления мероприятиями.

## pages/calendar.py
Страница календаря мероприятий.

- **Импорты:**
  - `streamlit as st` - Библиотека для создания веб-интерфейса.
  - `streamlit_calendar.calendar` - Компонент календаря.
  - `datetime` - Работа с датой и временем.
  - `ui.sidebar.render_sidebar` - Отрисовка боковой панели.
  - `database.database` - Множество функций для работы с базой данных мероприятий.

- **Константы:**
  - `CALENDAR_CONFIG` - Настройки календаря (тулбар, вид, локаль).

- **Функции:**
  - `setup_page()` - Настройка страницы, проверка авторизации.
  - `format_datetime(iso_string, timezone_offset)` - Форматирует ISO-дату в читаемый вид.
  - `add_event_form(selected_date)` - Форма добавления мероприятия с предустановленной датой.
  - `display_date_selection(selected_date)` - Отображает выбранную дату и кнопку для добавления мероприятия.
  - `edit_event_form(event)` - Форма редактирования мероприятия.
  - `display_event_details(event)` - Отображает детали мероприятия с опциями редактирования и удаления.
  - `render_calendar(events)` - Отрисовывает календарь и обрабатывает клики.
  - `main()` - Основная логика страницы, управляет отображением календаря.

## hash.py
Модуль для хеширования паролей.

- **Импорты:**
  - `hashlib` - Библиотека для хеширования.

- **Функции:**
  - `hash_password(password)` - Хеширует пароль с использованием SHA-256.

## database.py
Модуль для работы с базой данных SQLite.

- **Импорты:**
  - `sqlite3` - Работа с SQLite.
  - `datetime`, `timedelta` - Работа с датой и временем.
  - `hash.hash.hash_password` - Хеширование пароля.

- **Константы:**
  - `DB_NAME` - Путь к файлу базы данных.

- **Функции:**
  - `init_db()` - Инициализирует таблицы `users` и `events`.
  - `adjust_timezone(iso_time_str, hours)` - Корректирует время в ISO-формате.
  - `check_user(username, password_or_hash)` - Проверяет пользователя по имени и паролю/хешу.
  - `register_user(username, password)` - Регистрирует нового пользователя.
  - `add_event(username, title, start, end, color, description)` - Добавляет мероприятие.
  - `update_event(event_id, username, ...)` - Обновляет мероприятие.
  - `delete_event(event_id, username)` - Удаляет мероприятие.
  - `get_user_events_for_render_calendar(username)` - Возвращает события для календаря.
  - `get_user_events_for_change(username)` - Возвращает события для редактирования.
  - `get_event_by_id(event_id, username)` - Возвращает событие по ID.
  - `find_event_by_details(username, title, start, end)` - Находит событие по деталям.

## chat/chat_utils.py
Модуль для работы с чатом и обработки ввода.

- **Импорты:**
  - Множество библиотек: `os`, `json`, `time`, `logging`, `base64`, `typing`, `dotenv`, `huggingface_hub`, `gtts`, `streamlit`, `streamlit_chat`.

- **Константы:**
  - `CHAT_HISTORY_DIR` - Директория для хранения истории чата.

- **Функции:**
  - `load_chat_history(username)` - Загружает историю чата за последние 24 часа.
  - `save_chat_history(username, history)` - Сохраняет историю чата.
  - `clear_chat_history(username)` - Очищает историю чата.
  - `recognize_speech(audio_path)` - Распознает речь из аудиофайла через Hugging Face.
  - `text_to_speech(text)` - Преобразует текст в аудио с помощью gTTS.
  - `process_user_input(user_input, audio_data)` - Обрабатывает текстовый или аудиоввод.
  - `generate_bot_response(user_input, is_audio)` - Генерирует ответ бота.
  - `display_chat()` - Отображает историю чата в интерфейсе.

## .streamlit/config.toml
Конфигурация Streamlit.

- **Настройки:**
  - `[client]`
    - `showSidebarNavigation = false` - Отключает стандартную навигацию в боковой панели.

## .env
Файл переменных окружения.

- **Переменные:**
  - `HUGGINGFACE_TOKEN` - Токен для доступа к API Hugging Face.
  - `COOKIE_PASSWORD` - Пароль для шифрования куки.