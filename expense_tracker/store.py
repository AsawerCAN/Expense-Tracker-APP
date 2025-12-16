from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import Expense

DEFAULT_DB_PATH = Path("expenses.json")


class ExpenseStore:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self.expenses: List[Expense] = []

    def load(self) -> None:
        if not self.db_path.exists():
            self.expenses = []
            return

        try:
            raw = json.loads(self.db_path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("DB file must contain a JSON list.")
            self.expenses = [Expense.from_dict(item) for item in raw]
        except Exception as e:
            raise RuntimeError(f"Failed to load database '{self.db_path}': {e}") from e

    def save(self) -> None:
        data = [e.to_dict() for e in self.expenses]
        self.db_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_expense(self, expense: Expense) -> None:
        self.expenses.append(expense)
        self.save()

    def list_expenses(self) -> List[Expense]:
        return list(self.expenses)

    def total_spending(self, category: Optional[str] = None) -> float:
        if category is None:
            return sum(e.amount for e in self.expenses)

        cat = category.strip().lower()
        return sum(e.amount for e in self.expenses if e.category.lower() == cat)

    def clear_all(self) -> None:
        self.expenses = []
        self.save()
