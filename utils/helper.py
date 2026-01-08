# utils/helper.py
import re

def to_camel_case(s: str) -> str:
    """
    Convert snake_case or space separated string to camelCase.
    Examples:
        "doc_id" -> "docId"
        "expiry date" -> "expiryDate"
    """
    parts = re.split(r'[_\s]+', s)
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])


def dict_to_camel_case(data: dict) -> dict:
    """Convert all top-level keys of a dict to camelCase"""
    return {to_camel_case(k): v for k, v in data.items()}


def to_snake_case(s: str) -> str:
    """
    Convert camelCase string to snake_case.
    Examples:
        "docId" -> "doc_id"
        "expiryDate" -> "expiry_date"
    """
    s = re.sub(r'([A-Z])', r'_\1', s)
    return s.lower().lstrip('_')


def dict_to_snake_case(data: dict) -> dict:
    """Convert all top-level keys of a dict to snake_case"""
    return {to_snake_case(k): v for k, v in data.items()}
