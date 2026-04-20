## Тестовое задание на позицию Fullstack разработчика (Python + React)

**Вводные:**
1. Здесь представлен MVP проект файлообменника. Он позволяет загружать файлы, проверяет их на подозрительный контент и отправляет алерты;
2. Репозиторий содержит в себе бэкенд и фронтенд части;
3. В обоих частях присутствуют баги, неоптимизированный код, неудачные архитектурные решения.

**Задачи:**
1. Проведите рефакторинг бэкенда, не ломая бизнес-логики: предложите свое видение архитектуры и реализуйте его;
2. (Дополнительно) На бэкенде есть возможность неочевидной оптимизации - выполните ее;
3. (Дополнительно) Разбейте логику фронтенда на слои;

**Запуск:**
1. ```docker compose -f docker-compose.dev.yml up```
2. ```docker exec -it backend alembic upgrade head```


**Открыть фронт:** ```http://localhost:3000/test``` 

**Открыть бэк:** ```http://localhost:8000/docs```

---

## Что сделано

### Backend — архитектура (п.1)

Плоский `src/{app,service,tasks,models,schemas}.py` разложен по слоям и bounded-контекстам:

```
src/
├── core/        config (pydantic-settings), db (async+sync engines), storage (abstract), exceptions
├── files/       models, schemas, repository, service, router
├── alerts/      models, schemas, repository, service, router
├── tasks/       celery_app, scanner, metadata, pipeline
├── api/         deps (Depends), errors (DomainError → HTTP)
└── app.py       create_app(): middleware + routers + handlers
```

- Сервисы не зависят от FastAPI: бросают `FileNotFound` / `EmptyUpload` / `StoredBlobMissing`, единый handler в `api/errors.py` превращает их в HTTP.
- DI через `Depends(get_file_service)` собирает сервис из `AsyncSession` + `FileStorage` — в тестах подменяется одной строкой.
- `FileStorage` — абстрактный интерфейс, `LocalFileStorage` — реализация на ФС (завтра S3 — без правок сервиса).
- `Settings` (pydantic-settings) — единый источник правды; прямых `os.environ` больше нет.
- Роутеры вместо всего в одном `app.py`: `/files` и `/alerts` + `/health`.

### Backend — оптимизация (п.2)

Цепочка из трёх Celery-задач (`scan` → `extract_metadata` → `send_alert`) свёрнута в одну `process_uploaded_file` в `src/tasks/pipeline.py`.

| На 1 загруженный файл | Было | Стало |
| --- | --- | --- |
| Celery-задач | 3 | 1 |
| Broker round-trips | 3 | 1 |
| SELECT `StoredFile` | 3 | 1 |
| COMMIT | 3 | 1 |
| Event loop'ов в воркере | 1 глобальный (`_worker_loop` хак) | 0 |

Плюс:
- **sync SQLAlchemy в воркере** (`psycopg`): Celery prefork обрабатывает одну задачу на процесс, async там только добавлял оверхед и заставлял держать глобальный event loop.
- Параметры скана (`size`, `mime_type`, `extension`) передаются в task args — без лишнего SELECT ради неизменяемых полей.
- `scanner.scan` и `metadata.extract` — чистые функции, юнит-тестируются без ORM.

### Frontend — слои (п.3)

`page.tsx` на 367 строк → FSD-раскладка:

```
app/            layout, page (5 строк, только <FilesPage />)
widgets/        files-page
features/       upload-file, rename-file, delete-file, files-list, alerts-list
entities/       file (types + badges), alert (types + badge)
shared/         api/{client,files,alerts}, config/env, lib/format
```

- `shared/api/client.ts` — типизированный `apiFetch<T>` + `ApiError`, URL из `NEXT_PUBLIC_API_URL`.
- `useFiles` автоматически перечитывает список каждые 2s, пока есть файлы в `uploaded`/`processing`, и сам останавливается.
- Добавлены действия rename и delete (API их умел, в UI не было).

### Дополнительно

- **Streaming upload:** `LocalFileStorage.save` пишет чанками по 1 MiB — убрано `await upload_file.read()` в RAM.
- **CASCADE на `alerts.file_id`** + индекс: отдельная миграция. До этого `DELETE /files/{id}` падал FK violation при наличии алертов.
- **Compose:** healthchecks postgres/redis, отдельный `backend-migrate` (`condition: service_completed_successfully`) — `alembic upgrade head` руками больше не нужен. Исправлен порт БД (`5433:5432`) и исчезнувший `CELERY_BROKER_URL` (в оригинале читался несуществующий `REDIS_URL`).
- **Валидация** `title` 1..255 в Form и PATCH.
- **favicon:** исправлен битый путь `/public/favicon.ico`.
