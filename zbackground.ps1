# celery -A app.celery_app.celery worker --concurrency=4 --loglevel=info
celery -A app.config.celery_app.celery worker --pool=solo --loglevel=info
Write-Host "Started worker ..." -ForegroundColor Green
