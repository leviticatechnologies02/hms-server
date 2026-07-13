import re
from typing import Optional
from uuid import UUID


def validate_uuid(value: str) -> bool:
    """Validate UUID string."""
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number."""
    pattern = r'^\+?[\d\s-]{10,20}$'
    return bool(re.match(pattern, phone))


def validate_hospital_code(code: str) -> bool:
    """Validate hospital code."""
    pattern = r'^[A-Z0-9]{2,10}$'
    return bool(re.match(pattern, code))


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*()]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"