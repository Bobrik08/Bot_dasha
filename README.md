# Dasha Bot — учебный модератор чатов

Небольшой Telegram-бот на `aiogram 3`, который помогает модераторам:
- вести чёрный список пользователей;
- смотреть простую статистику;
- по команде проверять чат и банить тех, кто есть в чс.

Проект учебный, но бот можно запустить “по-взрослому” через Docker.

---

## Технологии

- Python 3.11+
- aiogram 3
- SQLAlchemy (async) + Alembic
- PostgreSQL (через Docker)
- pytest + pytest-asyncio + pytest-cov
- Docker / docker compose

---

## Структура проекта

- `main.py` — точка входа, создание `Bot` / `Dispatcher`, запуск.
- `config.py` — чтение настроек из `.env`, базовая конфигурация.
- `bot/handlers/` — обработчики команд и сообщений:
  - `start.py` — `/start`, приветствие и основная информация;
  - `admin.py` — админ-команды: `/adduser`, `/deluser`, `/stats`, `/force_check`;
  - `common.py` — простой echo-хендлер для “подстраховки” и отладки.
- `bot/database/`:
  - `connection.py` — создание async-engine, `init_db`;
  - `models.py` — модели SQLAlchemy для чёрного списка и логов;
  - `repository.py` — репозиторий `user_repo` для работы с пользователями;
  - `user.py` — учебная in-memory “база” (используется в тестах).
- `bot/handlers/__init__.py` — регистрация всех роутеров.
- `bot/database/__init__.py` — удобный экспорт `init_db`, моделей и репозитория.
- `alembic/` — миграции БД (в т.ч. `1_init_blacklist.py`).
- `dockerfile`, `docker-compose.yml` — описание докер-сервиса для бота и БД.
- `tests/` — тесты для хендлеров и репозитория.

---

## Переменные окружения

Используются через `.env` (локальный запуск) и/или `.env.docker` (для Docker):

- `BOT_TOKEN` — токен Telegram-бота (от @BotFather).
- `ADMIN_IDS` — список id админов, через запятую  
  пример:  
  `ADMIN_IDS=123456789,987654321`
- `DATABASE_URL` — строка подключения к БД  
  пример для Docker:  
  `DATABASE_URL=postgresql+asyncpg://bot:bot@db:5432/bot_db`
- `MODERATED_CHAT_IDS` — id чатов для фоновой проверки, через запятую  
  пример:  
  `MODERATED_CHAT_IDS=-100123,-100456`  
  если пусто — периодическая проверка не запускается, работает только `/force_check`.

---

## Запуск локально (без Docker)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows (PowerShell): .venv\Scripts\activate

pip install -r requirements.txt

# создать .env и заполнить переменные (BOT_TOKEN, ADMIN_IDS, DATABASE_URL и т.д.)
cp .env.docker .env  # опционально, как шаблон

# применить миграции (если используете Postgres/другую реальную БД)
alembic upgrade head

# запуск бота
python main.py
```

## Запуск через Docker

```bash
docker compose up --build

#остановить
docker compose down
```
## Команды бота

Общие
	•	/start — приветствие, краткое описание бота, подсказки по использованию.
	•	/help — (если включён) список доступных команд с короткими пояснениями.

Админские (только для id из ADMIN_IDS)
	•	/adduser <id>
Добавляет пользователя в чёрный список.
Можно вызвать в двух вариантах:
	•	/adduser 123456789 — напрямую по id;
	•	ответом на сообщение пользователя — id берётся из reply.
	•	/deluser <id>
Удаляет пользователя из чёрного списка.
Если id не в списке, бот просто сообщает, что такого нет.
	•	/stats
Показывает простую статистику:
	•	сколько пользователей сейчас в чёрном списке;
	•	сколько всего было действий (бан/разбан);
	•	последнюю операцию в текстовом виде.
	•	/force_check
Принудительная проверка текущего чата:
	•	берём список пользователей из чёрного списка;
	•	пытаемся их забанить в этом чате;
	•	в ответ отправляется небольшой отчёт с количеством забаненных id.


## Тесты и покрытие

```bash
#запуск всех тестов
pytest

#отчет по покрытию
pytest --cov=bot --cov=config --cov-report=term-missing
```


