from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


def now_utc():
    """Return aware UTC datetime."""
    return datetime.now(timezone.utc)


def now_ist():
    """Return aware IST datetime."""
    return datetime.now(IST)


def ist_to_utc(dt):
    """Convert aware or naive IST datetime to aware UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    return dt.astimezone(timezone.utc)


def parse_datetime(value):
    """Parse string or datetime into an aware IST datetime."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=IST) if value.tzinfo is None else value

    if isinstance(value, str):
        dt = datetime.fromisoformat(value)
        return dt.replace(tzinfo=IST)

    raise ValueError("Invalid datetime format")

def mongo_to_utc(value):
    """
    Convert MongoDB datetime (either $date or datetime) to aware UTC datetime.
    """
    # Case: {"$date": {"$numberLong": "1730000000000"}}
    if isinstance(value, dict) and "$date" in value:
        millis = int(value["$date"]["$numberLong"])
        return datetime.fromtimestamp(millis / 1000, tz=timezone.utc)

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    raise ValueError("Invalid datetime input for mongo_to_utc")
def utc_to_ist(dt):
    return dt.astimezone(IST)
