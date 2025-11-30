### tg-stream-service — асинхронный модульный Telegram-стример (RU)
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/1fb799d2-12bd-4ba3-bdde-3f9c67cb61cc" />


tg-stream-service — это лёгкий каркас на базе `Telethon` для получения сообщений из указанных чатов и последовательной обработки их набором подключаемых «агентов». Проект сфокусирован на простоте конфигурации (YAML), явной маршрутизации по чатам и расширяемости через реестр агентов.

#### Возможности
- Асинхронная работа на базе `Telethon`
- Маршрутизация: для каждого чата указываются один или несколько агентов
- Лёгкая расширяемость: агенты регистрируются в `agent_registry`
- Логирование в файл и консоль через настраиваемый `logging_setup`
- Поддержка прокси (через `httpx-socks`, при необходимости)
- Готовые примеры AI-агентов на базе `google-genai` (Gemini)

#### Требования
- Python `>= 3.13`
- Telegram API credentials (`api_id`, `api_hash`)

#### Установка
Вариант 1 (рекомендуется): `uv`
```bash
# Установите uv (если ещё не установлен)
pip install uv

# Создайте и активируйте виртуальное окружение
uv venv
. .venv/bin/activate  # Linux/macOS
# или
. .venv\Scripts\activate  # Windows PowerShell

# Установите зависимости из pyproject.toml / uv.lock
uv sync
```

Вариант 2: стандартный `pip`
```bash
python -m venv .venv
. .venv/bin/activate  # Linux/macOS
# или
. .venv\Scripts\activate  # Windows PowerShell

# Установите необходимые пакеты напрямую
pip install telethon pyyaml httpx httpx-socks google-genai clickhouse-connect
```

#### Конфигурация
1) Скопируйте пример и заполните значения:
```bash
cp config/config.example.yml config/config.yml
```
2) Отредактируйте `config/config.yml`. Пример минимальной структуры:
```yaml
telegram:
  api_id: 123456
  api_hash: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  session_name: ".sessions/my_session"
  # Ключи — идентификаторы чатов: @username, числовые ID, приглашения и т.п.
  # Значения — имя агента (строка) или список имён агентов
  chats:
    "@my_channel": ["log_writer", "noir_detective"]
    "-1001234567890": "gemini_analytic_LKOH"

logging:
  level: INFO           # опционально, можно управлять через запуск
  file: "log/tg_stream_service.log"
```
Замечания:
- Сессии `Telethon` будут сохранены в `.sessions/` (папка игнорируется в `.gitignore`).
- Реальный `config/config.yml` не коммится. Шаблон `config/config.example.yml` — в репозитории.

#### Запуск
```bash
python main.py
```
При запуске:
- инициализируется логирование (`log/tg_stream_service.log` + консоль),
- загружается конфиг,
- подключается клиент Telegram,
- регистрируются обработчики `events.NewMessage` для каждого чата и соответствующих агентов,
- приложение работает до отключения (`Ctrl+C`).

#### Как работает маршрутизация
Блок `telegram.chats` в конфиге ожидает:
- пустое значение — агенты не назначены;
- строку — один агент;
- список/кортеж — множество агентов. Дубликаты убираются.

В коде:
- `agent_registry` — словарь `str -> callable`, где ключ — имя агента, значение — асинхронная функция-обработчик `Telethon` события.
- Для каждой пары (чат, агент) регистрируется свой `events.NewMessage` хэндлер.

#### Добавление собственного агента
1) Создайте модуль в `packages/agents/`, например `my_agent.py`.
2) Зарегистрируйте обработчик в реестре с помощью декоратора или прямой записи. Рекомендуемый способ — декоратор `@agent_registration` из `packages.decorators.agent_registration`:
```python
# packages/agents/my_agent.py
import asyncio
from telethon import events
from packages.decorators.agent_registration import agent_registration


@agent_registration("my_agent")
async def my_agent_handler(
    event: events.NewMessage.Event,
    ai_provider,
    ch_provider,
    tg_provider,
):
    # ваш код обработки сообщения
    await event.reply("Processed by my_agent")
```
3) В `config/config.yml` добавьте имя агента для нужного чата:
```yaml
telegram:
  chats:
    "@my_channel": ["log_writer", "my_agent"]
```
4) Перезапустите приложение.

Готовые примеры в репозитории:
- `log_writer` — простой логирующий агент
- `noir_detective` — агент-ответчик в стиле «нуар» (Gemini)
- `gemini_analytic_LKOH` — аналитический агент для LKOH (Gemini + ClickHouse)

#### Логирование
Инициализация выполняется вызовом `logging_setup(log_file_path="log/tg_stream_service.log", level=logging.INFO)`. Журнал пишется в файл и выводится на консоль. Папка `log/` хранится в репозитории пустой через `log/.gitkeep`.

#### Безопасность и секреты
- Не коммитьте `config/config.yml`, файлы сессий `*.session`, содержимое `.sessions/` и `.env` — это уже учтено в `.gitignore`.
- Храните ключи API в локальном конфиге (`config.yml`) или переменных окружения, не в коде.

#### Отладка и типичные проблемы
- "Config file not found": проверьте путь `./config/config.yml` или передайте свой путь в конструктор `Application`.
- "The list of chats is empty": заполните `telegram.chats`.
- Ошибка Telegram API (`RPCError`): проверьте доступ к чату, валидность `api_id`/`api_hash` и состояние сети/прокси.
- Нет реакции на сообщения: убедитесь, что имя агента совпадает с ключом в `agent_registry` и чат указан корректно.

#### Провайдеры и жизненный цикл
- GoogleAIProvider — доступ к моделям Gemini через `google-genai` (ключ в `config.google_ai.api_key`).
- ClickhouseProvider — единоразовое подключение к ClickHouse при старте и повторное использование соединения для вставок.
- TelegramProvider — вспомогательный провайдер вокруг `Telethon` клиента.

Приложение выполняет:
1) загрузку конфигурации и нормализацию маршрутизации;
2) инициализацию провайдеров;
3) подключение к ClickHouse (`connect()`);
4) запуск `Telethon` клиента и регистрацию обработчиков для каждой пары (чат, агент).
