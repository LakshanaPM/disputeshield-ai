"""
DisputeShield AI — Celery Application

Initializes Celery with Redis broker and backend for async dispute processing.
"""

import sys
from pathlib import Path
from celery import Celery

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import settings

celery_app = Celery(
    "disputeshield",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tasks.dispute_processor"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=False,
    broker_connection_max_retries=1,
    task_publish_retry=False,
)

celery_app.autodiscover_tasks(["tasks", "backend.tasks"])
