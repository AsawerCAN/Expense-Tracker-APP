# main.py (entry point only)

from expense_tracker.models import Expense
from expense_tracker.store import ExpenseStore
from expense_tracker.utils import (
    parse_date,
    validate_amount,
    validate_category,
    validate_description,
    safe_int_input,
    safe_float_input,
)


def print_menu() -> None:
    print("\n==== Menu ====")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. View Total Spending")
    print("4. View Total By Category")
    print("5. Exit")


def format_expense(idx: int, e: Expense) -> str:
    return (
        f"{idx:>3}. {e.date.isoformat()} | "
        f"{e.category:<12} | {e.amount:>10.2f} | {e.description}"
    )


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

            store.add_expense(
                Expense(date=d, category=category, description=description, amount=amount)
            )
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
        store.clear_all()  # implement this in store.py (simple)

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
