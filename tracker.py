
import csv
import os
import shutil
from datetime import datetime
from decimal import Decimal, InvalidOperation
from collections import defaultdict

# ==========================================
# CONFIGURATION
# ==========================================

CSV_FILE = "expenses.csv"

FIELDS = [
    "ID",
    "Date",
    "Category",
    "Description",
    "Amount",
    "Currency",
    "Payment Method"
]

CATEGORIES = [
    "Groceries",
    "Transport",
    "Housing",
    "Utilities",
    "Restaurants",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Travel",
    "Other"
]

PAYMENT_METHODS = [
    "Cash",
    "Card",
    "Bank Transfer",
    "Other"
]


# ==========================================
# CSV DATABASE
# ==========================================

def initialize_database():
    """Create CSV file if it doesn't exist."""

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()


def load_expenses():
    """Load all expenses from CSV."""

    with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_expenses(expenses):
    """Save expenses to CSV."""

    with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(expenses)


def generate_id(expenses):
    """Generate a unique expense ID."""

    existing_ids = []

    for expense in expenses:
        try:
            existing_ids.append(int(expense["ID"]))
        except (ValueError, KeyError):
            continue

    return max(existing_ids, default=0) + 1


# ==========================================
# INPUT HELPERS
# ==========================================

def select_option(options, title):
    """Display options and return selection."""

    print(f"\n{title}")

    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")

    while True:
        choice = input("Select option: ").strip()

        try:
            index = int(choice) - 1

            if 0 <= index < len(options):
                return options[index]

        except ValueError:
            pass

        print("Invalid selection. Try again.")


def get_amount():
    """Get a valid positive expense amount."""

    while True:
        value = input("Amount: ").strip().replace(",", ".")

        try:
            amount = Decimal(value)

            if amount.is_finite() and amount > 0:
                return amount.quantize(Decimal("0.01"))

        except InvalidOperation:
            pass

        print("Please enter a valid positive amount.")


def get_date():
    """Get a valid expense date."""

    while True:
        value = input(
            f"Date (YYYY-MM-DD, default today "
            f"{datetime.today().strftime('%Y-%m-%d')}): "
        ).strip()

        if not value:
            return datetime.today().strftime("%Y-%m-%d")

        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime(
                "%Y-%m-%d"
            )
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")


# ==========================================
# EXPENSE MANAGEMENT
# ==========================================

def add_expense():
    """Add a new expense."""

    expenses = load_expenses()

    print("\n========== ADD EXPENSE ==========")

    expense_id = generate_id(expenses)
    date = get_date()
    category = select_option(CATEGORIES, "Select category")

    description = input("Description: ").strip()

    while not description:
        print("Description cannot be empty.")
        description = input("Description: ").strip()

    amount = get_amount()

    currency = input("Currency (default EUR): ").strip().upper()
    currency = currency or "EUR"

    payment_method = select_option(
        PAYMENT_METHODS,
        "Select payment method"
    )

    new_expense = {
        "ID": expense_id,
        "Date": date,
        "Category": category,
        "Description": description,
        "Amount": str(amount),
        "Currency": currency,
        "Payment Method": payment_method
    }

    expenses.append(new_expense)
    save_expenses(expenses)

    print("\nExpense successfully added!")


def display_expenses(expenses):
    """Display expenses in a readable table."""

    if not expenses:
        print("\nNo expenses found.")
        return

    print("\n" + "=" * 105)

    print(
        f"{'ID':<5}"
        f"{'Date':<13}"
        f"{'Category':<17}"
        f"{'Description':<25}"
        f"{'Amount':>12}"
        f"{'Currency':>10}"
        f"{'Payment':>18}"
    )

    print("-" * 105)

    for expense in expenses:
        print(
            f"{expense['ID']:<5}"
            f"{expense['Date']:<13}"
            f"{expense['Category']:<17}"
            f"{expense['Description'][:23]:<25}"
            f"{expense['Amount']:>12}"
            f"{expense['Currency']:>10}"
            f"{expense['Payment Method']:>18}"
        )

    print("=" * 105)
    print(f"Total records: {len(expenses)}")


def view_expenses():
    """Display all expenses."""

    expenses = load_expenses()

    expenses.sort(key=lambda x: (x["Date"], int(x["ID"])))

    print("\n========== ALL EXPENSES ==========")
    display_expenses(expenses)


def search_expenses():
    """Search expenses by description or category."""

    expenses = load_expenses()

    query = input(
        "\nEnter search term (description/category): "
    ).strip().lower()

    if not query:
        print("Search term cannot be empty.")
        return

    results = [
        expense for expense in expenses
        if query in expense["Description"].lower()
        or query in expense["Category"].lower()
    ]

    print("\n========== SEARCH RESULTS ==========")
    display_expenses(results)


def show_summary():
    """Display expense statistics."""

    expenses = load_expenses()

    if not expenses:
        print("\nNo expenses available.")
        return

    totals = defaultdict(Decimal)
    category_totals = defaultdict(Decimal)
    count = defaultdict(int)

    for expense in expenses:
        currency = expense["Currency"]
        amount = Decimal(expense["Amount"])

        totals[currency] += amount
        category_totals[(expense["Category"], currency)] += amount
        count[currency] += 1

    print("\n========== EXPENSE SUMMARY ==========")

    for currency, total in sorted(totals.items()):
        print(f"\nCurrency: {currency}")
        print(f"Total expenses: {total:.2f}")
        print(f"Number of transactions: {count[currency]}")

        print("\nExpenses by category:")

        for (category, curr), amount in sorted(category_totals.items()):
            if curr == currency:
                print(f"  {category:<20} {amount:>12.2f} {currency}")


def delete_expense():
    """Delete an expense by ID."""

    expenses = load_expenses()

    expense_id = input("\nEnter expense ID to delete: ").strip()

    matching = [
        expense for expense in expenses
        if expense["ID"] == expense_id
    ]

    if not matching:
        print("Expense ID not found.")
        return

    print("\nExpense to delete:")
    display_expenses(matching)

    confirmation = input(
        "\nAre you sure you want to delete it? (y/n): "
    ).strip().lower()

    if confirmation == "y":
        expenses = [
            expense for expense in expenses
            if expense["ID"] != expense_id
        ]

        save_expenses(expenses)
        print("Expense deleted successfully.")
    else:
        print("Deletion cancelled.")


def export_expenses():
    """Export expenses to another CSV file."""

    filename = input(
        "\nEnter export filename (default expenses_export.csv): "
    ).strip()

    filename = filename or "expenses_export.csv"

    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    if os.path.abspath(filename) == os.path.abspath(CSV_FILE):
        print("Cannot export over the main database file.")
        return

    if os.path.exists(filename):
        confirmation = input(
            "File already exists. Overwrite? (y/n): "
        ).strip().lower()

        if confirmation != "y":
            print("Export cancelled.")
            return

    shutil.copyfile(CSV_FILE, filename)

    print(f"Expenses exported successfully to {filename}")


# ==========================================
# MAIN MENU
# ==========================================

def main():

    initialize_database()

    while True:

        print("\n")
        print("=" * 40)
        print("       PERSONAL EXPENSE TRACKER")
        print("=" * 40)

        print("1. Add a new expense")
        print("2. View all expenses")
        print("3. Search expenses")
        print("4. Show expense summary")
        print("5. Delete an expense")
        print("6. Export expenses to CSV")
        print("0. Exit")

        print("=" * 40)

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense()

        elif choice == "2":
            view_expenses()

        elif choice == "3":
            search_expenses()

        elif choice == "4":
            show_summary()

        elif choice == "5":
            delete_expense()

        elif choice == "6":
            export_expenses()

        elif choice == "0":
            print("\nBye!")
            break

        else:
            print("\nInvalid option. Please try again.")



if __name__ == "__main__":
    main()
