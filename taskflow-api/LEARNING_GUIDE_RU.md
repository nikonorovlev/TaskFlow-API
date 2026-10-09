# Как устроен TaskFlow API

## Путь запроса

1. Клиент отправляет JSON в `POST /api/v1/tasks/`.
2. FastAPI использует `TaskCreate` из `app/schemas/task.py`, чтобы проверить типы, длину названия и допустимые значения статуса и приоритета.
3. Маршрут в `app/api/routes/tasks.py` получает сессию SQLAlchemy через `Depends(get_db)`.
4. `app/services/task_service.py` создаёт ORM-объект `Task`, выполняет `add`, `commit` и `refresh`.
5. SQLAlchemy записывает данные в SQLite согласно модели `app/models/task.py`.
6. FastAPI сериализует объект через `TaskResponse` и возвращает HTTP 201.

## Назначение файлов

- `main.py`: создание FastAPI, маршруты, lifespan, health.
- `core/config.py`: настройки из окружения и `.env`.
- `db/database.py`: engine, sessionmaker, Base, создание таблиц, get_db.
- `models/task.py`: описание столбцов таблицы tasks.
- `schemas/task.py`: Pydantic-модели TaskCreate, TaskUpdate, TaskResponse, TaskStats; Enum статусов и приоритетов.
- `services/task_service.py`: CRUD, фильтрация, сортировка, статистика.
- `api/routes/tasks.py`: HTTP-маршруты и обработка 404.
- `api/routes/stats.py`: статистика.
- `tests/conftest.py`: отдельная тестовая БД и подмена зависимости get_db.
- `tests/test_tasks.py`: тесты API и ошибок.

## Важные конструкции

- `Mapped[T]` и `mapped_column()` описывают ORM-поля.
- `BaseModel` проверяет JSON и преобразует типы.
- `model_dump()` создаёт словарь из схемы.
- `model_dump(exclude_unset=True)` позволяет PATCH менять только присланные поля.
- `Depends(get_db)` внедряет сессию и закрывает её после запроса.
- `db.commit()` фиксирует транзакцию, `db.refresh()` перечитывает ORM-объект.
- `select(Task).where(...)` строит SQL-запрос, а `limit/offset` реализуют пагинацию.
- `response_model` задаёт формат ответа и документацию OpenAPI.

## Практика

1. Запусти `python -m uvicorn app.main:app --reload`.
2. Открой `/docs`, создай задачу POST и посмотри ответ 201.
3. Получи задачу GET по id; затем измени PATCH и удали DELETE.
4. Отправь неверный status и убедись, что получен 422.
5. Запусти `python -m pytest -v` и `ruff check .`.
6. Добавь собственный тест: фильтрация по дедлайну, проверка сортировки или очищение описания.

## Ограничения

Проект предназначен для локального обучения. Нет авторизации, миграций, ограничений скорости и защиты от публичного изменения чужих задач. Не разворачивай его в открытом интернете без доработки безопасности.
