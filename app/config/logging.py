import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Get project root based on this file location
BASE_DIR = Path(__file__).resolve().parent.parent.parent
logs_dir = BASE_DIR / "logs"

def init_logging_system():
    print("Logs directory will be:", logs_dir)

    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Get only warnings
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = TimedRotatingFileHandler(
        logs_dir / "app.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

init_logging_system()