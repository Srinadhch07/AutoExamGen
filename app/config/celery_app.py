from celery import Celery
import ssl
REDIS_URL = "redis://localhost:6379/0"
# REDIS_URL="rediss://default:AU3FAAIncDI1YWQ1OGRlOWZjZDQ0N2Q4YWFlN2Y4MTVjMGEzOTlkNHAyMTk5MDk@glad-liger-19909.upstash.io:6380/0"

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery.conf.imports = (
    "app.tasks.pdf_tasks",
)
celery.conf.update(
    # broker_use_ssl={
    #     "ssl_cert_reqs": ssl.CERT_NONE
    # },
    # redis_backend_use_ssl={
    #     "ssl_cert_reqs": ssl.CERT_NONE
    # },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    broker_pool_limit=1,
    task_track_started=True,
    task_send_sent_event=True,
)
