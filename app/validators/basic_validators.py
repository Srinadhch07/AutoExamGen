
import re
from bson.objectid import ObjectId
from bson.errors import InvalidId

from email_validator import validate_email, EmailNotValidError

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def is_strong_password(password: str) -> bool:
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,128}$'
    return bool(re.match(pattern, password))

def is_valid_name(name: str) -> bool:
    pattern = r'^[A-Za-z ]{1,100}$'
    return bool(re.match(pattern, name))

def is_valid_phone(phone: str) -> bool:
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

def is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False

def validate_date(date_str):

    pattern = r'^(?:\d{4})-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$'
    if re.match(pattern, date_str):
        return True
    return False

def is_string(value):
    if not isinstance(value, str):
        return False
    pattern = r'^[A-Za-z\s]+$'
    return bool(re.match(pattern, value))

def is_valid_id(value):
    try:
        ObjectId(value)
        return True
    except (InvalidId, TypeError):
        return False
def is_natural_number(value):

    if not isinstance(value, str):
        value = str(value)
    pattern = r'^[1-9]\d*$'
    return bool(re.match(pattern, value))

def is_valid_address(value):

    if not isinstance(value, str):
        return False
    value = value.strip()
    if len(value) < 5:
        return False
    pattern = r'^[A-Za-z0-9\s,.\-/#]+$'
    return bool(re.match(pattern, value))

def is_valid_time(time_str: str) -> bool:
    pattern = r"^([01]\d|2[0-3]):([0-5]\d)$"
    return bool(re.match(pattern, time_str))