import sys
import csv
import os
from typing import List
from datetime import datetime
from program.transaction_class import AccountInformation, Transaction
from program.constants import ALL_TRANSACTIONS, CONFIG, Tag
from program.helper_functions import check_descriptions, get_tag, print_warning_message, print_info_message


def get_file_names(directory: str = "./data") -> List[str]:
    """Get name of files located in the /data directory."""
    file_names = [
        file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file)) and ".csv" in file
    ]
    file_names.remove("budget.csv")
    return file_names


def import_data(directory: str) -> None:
    """Import data from .csv files exported from bank website into defined classes."""
    file_names = get_file_names(directory)
    ALL_TRANSACTIONS.clear()
    for file_name in file_names:
        account_id = None
        for config in CONFIG["Accounts"]:
            if config["Keyword"] in file_name:
                account_id = config["Id"]
                break
        assert account_id is not None, f"No account id found for file: {file_name}"
        current_account = AccountInformation(file_name, [])
        ap = CONFIG["Accounts"][account_id]["ORM Information"]  # account prefix

        with open(f"{directory}/{file_name}", "r", encoding="UTF-8", errors="replace") as file:
            delimiter = ap["Delimiter"]
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            for row in csv_reader:
                try:
                    date = datetime.strptime(row[ap["Date"]], ap["Date Format"])
                    currency = row[ap["Currency"]] if "Currency" in ap else "USD"
                    bank = CONFIG["Accounts"][account_id]["Bank Name"]
                    account = CONFIG["Accounts"][account_id]["Account Type"].replace(" ", "_")
                    description = (
                        f'{row[ap["Description"]]}'
                        if "Transaction type" not in row
                        else f'{row[ap["Description"]]} {row[ap["Transaction Type"]]}'
                    )
                    description = description.replace(";", "")

                    if "Amount" not in ap:
                        debit = float(row["Debit"]) if row["Debit"] else 0.0
                        credit = float(row["Credit"]) if row["Credit"] else 0.0
                        amount = credit if credit != 0.0 else -debit
                    else:
                        amount = float(row[ap["Amount"]].replace(",", ".").replace(" ", ""))

                except ValueError:
                    print_warning_message(f"Error parsing row: {row}")

                current_account.transactions.append(
                    Transaction(
                        description=description, date=date, amount=amount, currency=currency, bank=bank, account=account
                    )
                )
        ALL_TRANSACTIONS[account_id] = current_account


def format_data() -> None:
    """For each transaction in each account create a budget transaction item."""
    for account in ALL_TRANSACTIONS.keys():
        transactions = ALL_TRANSACTIONS[account].transactions
        for transaction in transactions:
            check_descriptions(transaction)


def show_all_transactions(transactions: list) -> None:
    for n, item in enumerate(transactions):
        if item.tag:
            print(
                f'{n} \t {item.amount:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.bank} \t {item.account.value} \t {item.tag.value} \t {item.description}'
            )
        else:
            print_info_message(
                f'{n} \t {item.amount:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.bank} \t {item.account.value} \t NULL \t {item.description}'
            )


def edit_data() -> None:
    """Display the budget items to the user for review and allow them to edit the items."""
    for account in ALL_TRANSACTIONS.keys():
        transactions = ALL_TRANSACTIONS[account].transactions
        show_all_transactions(transactions)
        while True:
            item_number = input("Enter item number to edit (enter to continue): ")
            if item_number in ["", None]:
                break
            else:
                try:
                    item_number = int(item_number)
                except ValueError:
                    print_warning_message("Invalid input. Please enter a number.")
                    continue
                item = transactions[item_number]
                print(
                    f'{item.amount:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.tag.value} \t {item.account.value} \t {item.description}'
                )
                tag = get_tag()
                desc = input("\tEnter description: ")
                response = input(f"Is item {item_number} correct? Type 'Y' to save or any character to discard.")
                desc = desc if desc not in ["", None] else item.description
                print(
                    f'{item.amount:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {tag.value} \t {item.account.value} \t {desc}'
                )

                if response.lower() == "y":
                    item.tag = Tag(tag)
                    item.description = desc
                else:
                    print("Item discarded.")

                show_transactions = input("Show all transactions? (Y/N): ")
                if show_transactions.lower() == "y":
                    show_all_transactions(transactions)


def insert_data_to_file(directory: str) -> None:
    """Insert budget items into budget.csv file."""
    for account in ALL_TRANSACTIONS.keys():
        budget_items = ALL_TRANSACTIONS[account].transactions
        sorted_budget_items = sorted(budget_items, key=lambda x: x.date)
        for item in sorted_budget_items:
            with open(f"{directory}/budget.csv", "a") as file:
                csv_writer = csv.writer(file)
                if item.tag:
                    csv_writer.writerow(
                        [
                            item.date.strftime("%Y-%m-%d"),
                            item.bank,
                            item.account.value,
                            item.amount,
                            item.tag.value,
                            item.description,
                        ]
                    )


def cleanup():
    # Perform cleanup operations here, e.g., closing files, releasing resources, etc.
    ALL_TRANSACTIONS.clear()


def signal_handler(sig, frame):
    print("\nCtrl+C detected. Cleaning up...")
    cleanup()
    sys.exit(0)
