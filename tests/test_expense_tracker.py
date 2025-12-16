import json
from pathlib import Path
import pytest
from datetime import date

from expense_tracker.models import Expense
from expense_tracker.store import ExpenseStore
from expense_tracker.utils import parse_date


def test_parse_date_valid():
    assert parse_date("2025-12-16") == date(2025, 12, 16)


def test_parse_date_invalid():
    assert parse_date("16-12-2025") is None
    assert parse_date("") is None


def test_add_and_total(tmp_path: Path):
    db = tmp_path / "expenses.json"
    store = ExpenseStore(db)

    store.load()
    assert store.total_spending() == 0

    store.add_expense(Expense(date=date(2025, 12, 16), category="food", description="burger", amount=10.5))
    store.add_expense(Expense(date=date(2025, 12, 16), category="travel", description="bus", amount=3.0))

    assert store.total_spending() == pytest.approx(13.5)
    assert store.total_spending(category="food") == pytest.approx(10.5)
    assert store.total_spending(category="FOOD") == pytest.approx(10.5)


def test_persistence(tmp_path: Path):
    db = tmp_path / "expenses.json"

    store1 = ExpenseStore(db)
    store1.expenses = []
    store1.add_expense(Expense(date=date(2025, 12, 16), category="food", description="rice", amount=5.0))

    store2 = ExpenseStore(db)
    store2.load()
    assert len(store2.list_expenses()) == 1
    assert store2.total_spending() == pytest.approx(5.0)


def test_corrupt_db_raises(tmp_path: Path):
    db = tmp_path / "expenses.json"
    db.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

    store = ExpenseStore(db)
    with pytest.raises(RuntimeError):
        store.load()
