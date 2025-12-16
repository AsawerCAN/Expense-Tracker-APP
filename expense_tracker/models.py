from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from typing import Dict, Any

from .utils import parse_date, validate_amount, validate_category, validate_description


@dataclass(frozen=True)
class Expense:
    date: date
    category: str
    description: str
    amount: float

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Expense":
        d = parse_date(str(data.get("date", "")).strip())
        if d is None:
            raise ValueError(f"Invalid date in file: {data.get('date')}")

        category = str(data.get("category", "")).strip()
        description = str(data.get("description", "")).strip()

        try:
            amount = float(data.get("amount"))
        except (TypeError, ValueError):
            raise ValueError(f"Invalid amount in file: {data.get('amount')}")

        validate_category(category)
        validate_description(description)
        validate_amount(amount)

        return Expense(date=d, category=category, description=description, amount=amount)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["date"] = self.date.isoformat()
        return payload
