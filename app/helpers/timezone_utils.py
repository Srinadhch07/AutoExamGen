from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))

def now_utc():
    return datetime.now(timezone.utc)

def now_ist():
    return datetime.now(IST)

def ist_to_utc(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    return dt.astimezone(timezone.utc)

def parse_datetime(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=IST) if value.tzinfo is None else value
    if isinstance(value, str):
        dt = datetime.fromisoformat(value)
        return dt.replace(tzinfo=IST)

    raise ValueError("Invalid datetime format")
