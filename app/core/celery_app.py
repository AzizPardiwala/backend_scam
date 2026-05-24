from celery import Celery
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv(override=True)

REDIS_URL = os.getenv("REDIS_URL", "")

print(f"DEBUG REDIS_URL = '{REDIS_URL}'")  # temporary debug line

if not REDIS_URL:
    raise ValueError("REDIS_URL is not set in .env file")

celery_app = Celery(
    "scam_detection",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.scam_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
