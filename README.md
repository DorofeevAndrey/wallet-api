**Wallet API**

Короткое описание

- Небольшой сервис на FastAPI для работы с кошельками: получение баланса и операции (DEPOSIT / WITHDRAW).

Ключевые файлы

- **API:** [app/api/v1/wallets.py](app/api/v1/wallets.py#L1-L39)
- **Точка входа:** [app/main.py](app/main.py#L1-L8)
- **Docker Compose:** [docker-compose.yml](docker-compose.yml)
- **Dockerfile:** [Dockerfile](Dockerfile)
- **Тесты:** [tests/test_api.py](tests/test_api.py)

Требования

- Docker и Docker Compose (инструкции для Docker Desktop или Docker CLI)
- Python 3.12 (для локального запуска и тестов)

Быстрый старт (через Docker Compose)

1. Скопировать пример окружения и отредактировать значения:

```bash
cp .env.example .env    # Unix/macOS
copy .env.example .env  # Windows (PowerShell/CMD)
```

Файл `.env.example` содержит переменные: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`.

2. Поднять сервисы и выполнить миграции:

```bash
docker compose up --build
```

Это создаст БД, применит миграции (сервис `migrations`) и запустит приложение на порту 8000.

После запуска доступно:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Запуск тестов через Docker Compose

Проект содержит сервис `tests` в `docker-compose.yml`, который запускает `pytest` после применения миграций. Чтобы запустить тесты через Docker Compose и получить корректный код выхода, используйте:

```bash
docker compose up --build --exit-code-from tests tests
```

Команда соберёт образы, выполнит миграции и затем запустит тесты внутри контейнера `tests`. Контейнеры завершатся после завершения тестов, а команда вернёт код выхода тестов (0 при успехе).

Локальные тесты (venv)

1. Создать и активировать виртуальное окружение (опционально):

```bash
python -m venv .venv
source .venv/bin/activate   # Unix/macOS
.venv\Scripts\activate    # Windows PowerShell
```

2. Установить зависимости для тестов:

```bash
python -m pip install pytest pytest-asyncio httpx
```

3. Запустить тесты:

```bash
pytest -q
```
