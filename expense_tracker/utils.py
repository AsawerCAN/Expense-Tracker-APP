from __future__ import annotations

from datetime import datetime, date
from typing import Optional


def parse_date(value: str) -> Optional[date]:
    """
    Parse YYYY-MM-DD into a date object.
    Return None if invalid.
    """
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def validate_amount(amount: float) -> None:
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")


def validate_category(category: str) -> None:
    category = category.strip()
    if not category:
        raise ValueError("Category cannot be empty.")
    if len(category) > 30:
        raise ValueError("Category too long (max 30 characters).")


def validate_description(description: str) -> None:
    description = description.strip()
    if not description:
        raise ValueError("Description cannot be empty.")
    if len(description) > 120:
        raise ValueError("Description too long (max 120 characters).")


def safe_int_input(prompt: str) -> Optional[int]:
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        return None


def safe_float_input(prompt: str) -> Optional[float]:
    raw = input(prompt).strip()
    try:
        return float(raw)
    except ValueError:
        return None
