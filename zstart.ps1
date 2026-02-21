Write-host "Starting project... in  5 secs" -ForegroundColor Green
uvicorn main:app --reload  --port 8000
# uvicorn main:app --host 0.0.0.0 --port 8080 --log-level critical