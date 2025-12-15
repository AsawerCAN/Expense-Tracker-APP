# Personal Finance App / main.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Any


DEFAULT_DB_PATH = Path("expenses.json")


@dataclass(frozen=True)
class Expense:
    date: date
    category: str
    description: str
    amount: float

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Expense":
        # Defensive parsing for file-loaded data
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
        payload["date"] = self.date.isoformat()  # store as YYYY-MM-DD
        return payload


class ExpenseStore:
    """
    Handles expense list + persistence.
    Keeping this separate makes it testable and keeps UI clean.
    """
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
            # In real apps you’d log this; for a CLI, we show a helpful error.
            raise RuntimeError(f"Failed to load database '{self.db_path}': {e}") from e

    def save(self) -> None:
        data = [e.to_dict() for e in self.expenses]
        self.db_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_expense(self, expense: Expense) -> None:
        self.expenses.append(expense)
        self.save()

    def total_spending(self, category: Optional[str] = None) -> float:
        if category is None:
            return sum(e.amount for e in self.expenses)
        cat = category.strip().lower()
        return sum(e.amount for e in self.expenses if e.category.lower() == cat)

    def list_expenses(self) -> List[Expense]:
        # return a copy so caller can’t accidentally mutate internal list
        return list(self.expenses)


# -----------------------------
# Validation + parsing helpers
# -----------------------------

def parse_date(value: str) -> Optional[date]:
    """
    Accepts YYYY-MM-DD (recommended).
    Returns None if invalid.
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
    if not category:
        raise ValueError("Category cannot be empty.")
    if len(category) > 30:
        raise ValueError("Category too long (max 30 characters).")


def validate_description(description: str) -> None:
    if not description:
        raise ValueError("Description cannot be empty.")
    if len(description) > 120:
        raise ValueError("Description too long (max 120 characters).")


def safe_int_input(prompt: str) -> Optional[int]:
    """
    Reads an int safely. Returns None if invalid.
    """
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        return None


def safe_float_input(prompt: str) -> Optional[float]:
    """
    Reads a float safely. Returns None if invalid.
    """
    raw = input(prompt).strip()
    try:
        return float(raw)
    except ValueError:
        return None


# -----------------------------
# CLI (UI) layer
# -----------------------------

def print_menu() -> None:
    print("\n==== Menu ====")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. View Total Spending")
    print("4. View Total By Category")
    print("5. Exit")


def format_expense(idx: int, e: Expense) -> str:
    return f"{idx:>3}. {e.date.isoformat()} | {e.category:<12} | {e.amount:>10.2f} | {e.description}"


def add_expense_flow(store: ExpenseStore) -> None:
    while True:
        d_raw = input("Enter date (YYYY-MM-DD): ").strip()
        d = parse_date(d_raw)
        if d is None:
            print("Invalid date. Use YYYY-MM-DD (example: 2025-12-16).")
            continue

        category = input("Enter category (e.g., food, travel): ").strip()
        description = input("Enter description: ").strip()
        amount = safe_float_input("Enter amount: ")

        try:
            if amount is None:
                raise ValueError("Amount must be a number.")
            validate_category(category)
            validate_description(description)
            validate_amount(amount)

            store.add_expense(Expense(date=d, category=category, description=description, amount=amount))
            print("Expense added successfully.")
            return
        except ValueError as e:
            print(f"Error: {e}")
            print("Please try again.\n")


def view_expenses_flow(store: ExpenseStore) -> None:
    items = store.list_expenses()
    if not items:
        print("No expenses added yet.")
        return

    print("\nList of all expenses:")
    for i, e in enumerate(items, start=1):
        print(format_expense(i, e))


def total_spending_flow(store: ExpenseStore) -> None:
    total = store.total_spending()
    print(f"\nTotal spending: {total:.2f}")


def total_by_category_flow(store: ExpenseStore) -> None:
    category = input("Enter category to filter: ").strip()
    if not category:
        print("Category cannot be empty.")
        return
    total = store.total_spending(category=category)
    print(f"Total spending for '{category}': {total:.2f}")


def main() -> None:
    print("Welcome to Expense Tracker")

    store = ExpenseStore()
    try:
        store.load()
    except RuntimeError as e:
        print(e)
        print("Starting with an empty list (your DB file may be corrupted).")
        store.expenses = []

    while True:
        print_menu()
        choice = safe_int_input("Please enter your choice: ")

        if choice is None:
            print("Invalid input. Enter a number like 1, 2, 3...")
            continue

        if choice == 1:
            add_expense_flow(store)
        elif choice == 2:
            view_expenses_flow(store)
        elif choice == 3:
            total_spending_flow(store)
        elif choice == 4:
            total_by_category_flow(store)
        elif choice == 5:
            print("Thanks for using Expense Tracker.")
            break
        else:
            print("Invalid choice. Pick from 1 to 5.")


if __name__ == "__main__":
    main()
