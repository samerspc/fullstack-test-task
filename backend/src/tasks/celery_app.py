from celery import Celery

from src.core.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "file_tasks",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_broker_url,
    include=["src.tasks.pipeline"],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)
