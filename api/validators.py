import re
from rest_framework import status
from rest_framework.response import Response


def validate_password_strength(password):
    """
    Password must:
    - Be at least 8 characters
    - Contain at least 1 uppercase letter
    - Contain at least 1 lowercase letter
    - Contain at least 1 number
    - Contain at least 1 special character
    """
    errors = []

    if len(password) < 8:
        errors.append("At least 8 characters")

    if not re.search(r'[A-Z]', password):
        errors.append("At least 1 uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("At least 1 lowercase letter")

    if not re.search(r'[0-9]', password):
        errors.append("At least 1 number")

    if not re.search(r'[!@#$%^&*(),.?\":{}|<>_\-+=~`\[\];/\'\\]', password):
        errors.append("At least 1 special character (!@#\$%^&*)")

    if errors:
        return False, errors

    return True, []