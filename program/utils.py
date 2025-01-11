import sys
import csv
import os
from typing import List
from datetime import datetime
import requests
from ai.model import BertTextClassifier
from program.transaction_class import AccountInformation, Transaction
from program.constants import ALL_TRANSACTIONS, CONFIG, Tags
from program.helper_functions import (
    check_description,
    get_tag,
    print_warning_message,
    print_info_message,
)


def get_file_names(directory: str = "./data") -> List[str]:
    """Get name of files located in the /data directory."""
    file_names = [
        file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file)) and ".csv" in file
    ]
    try:
        file_names.remove("budget.csv")
    except ValueError:
        pass
    return file_names


def import_data(directory: str) -> None:
    """Import data from .csv files exported from bank website into defined classes."""
    file_names = get_file_names(directory)
    ALL_TRANSACTIONS.clear()
    for file_name in file_names:
        account_id = None
        for config in CONFIG.accounts:
            if config["keyword"] in file_name:
                account_id = config["id"]
                break
        assert account_id is not None, f"No account id found for file: {file_name}"
        current_account = AccountInformation(file_name, [])
        ap = CONFIG.accounts[account_id]["ormInformation"]  # account prefix

        with open(f"{directory}/{file_name}", "r", encoding="UTF-8", errors="replace") as file:
            delimiter = ap["delimiter"]
            csv_reader = csv.DictReader(file, delimiter=delimiter)

            check_for_duplicate_column_names(file_name, csv_reader)

            for row in csv_reader:
                try:
                    date = datetime.strptime(row[ap["date"]], ap["dateFormat"])
                    currency_code = ap["currencyCode"]
                    bank = CONFIG.accounts[account_id]["bankName"]
                    account_name = CONFIG.accounts[account_id]["accountType"].replace(" ", "_")

                    description = row[ap["description"]].replace(";", "")
                    if description in ["", None]:
                        description = (
                            row[ap["secondDescription"]]
                            + " "
                            + row[ap["thirdDescription"]]
                            + " "
                            + row[ap["fourthDescription"]]
                        )
                    description = description.strip()

                    # TODO fix this -_-
                    if ap["amount"] == "Credit/Debit":  # For account id 2
                        debit = float(row["Debit"]) if row["Debit"] else 0.0
                        credit = float(row["Credit"]) if row["Credit"] else 0.0
                        amount = credit if credit != 0.0 else -debit
                    elif ap["amount"] == "Transaction Amount":  # For account id 1
                        amount = (
                            float(row[ap["amount"]])
                            if row[ap["transactionType"]] == "Credit"
                            else -float(row[ap["amount"]])
                        )
                    else:
                        amount = float(row[ap["amount"]].replace(",", ".").replace(" ", ""))

                except ValueError:
                    print_warning_message(f"Error parsing row: {row} in file: {file_name}.")

                current_account.transactions.append(
                    Transaction(
                        description=description,
                        date=date,
                        amount_account_currency=amount,
                        account_currency=currency_code,
                        bank_name=bank,
                        account=account_name,
                        amount_usd=round(amount / get_exchange_rate(currency_code, is_test=bank), 2),
                    )
                )
        ALL_TRANSACTIONS[account_id] = current_account


def format_and_tag_data() -> None:
    """For each transaction in each account create a budget transaction item."""
    for account in ALL_TRANSACTIONS.keys():
        transactions = ALL_TRANSACTIONS[account].transactions
        features = [f"{t.amount_account_currency} {t.description}" for t in transactions]
        model = BertTextClassifier.load("private/saved_model")
        predictions = model.predict(features)
        assert len(transactions) == len(predictions), "Length mismatch between transactions and predictions."
        for transaction, prediction in zip(transactions, predictions):
            transaction.tag = Tags(prediction)
            check_description(transaction)


def show_paged_transactions(transactions: list, current_page=0) -> int:
    page_size = 15  # Number of items to show per page
    total_transactions = len(transactions)

    while current_page * page_size < total_transactions:
        start_index = current_page * page_size
        end_index = start_index + page_size
        for n, item in enumerate(transactions[start_index:end_index], start=start_index):
            if item.tag:
                print(
                    f'{n} \t {item.amount_account_currency:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.bank_name} \t {item.account.value} \t {item.tag.name} \t {item.description}'
                )
            else:
                print(
                    f'{n} \t {item.amount_account_currency:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.bank_name} \t {item.account.value} \t NULL \t {item.description}'
                )

        return current_page + 1


def review_data() -> None:
    """Display the budget items to the user for review and allow them to edit the items."""
    for account in ALL_TRANSACTIONS.keys():
        transactions = ALL_TRANSACTIONS[account].transactions
        show_paged_transactions(transactions)
        page = 0
        while True:
            user_input = input("Enter item number to edit, q to quit, or n for next items: ").strip()
            if user_input in ["q", "Q"]:
                break
            elif user_input in ["n", "N"]:
                page += 1
                show_paged_transactions(transactions, page)
            else:
                try:
                    user_input = int(user_input)
                except ValueError:
                    print_warning_message("Invalid input. Please enter a number.")
                    continue
                item = transactions[user_input]
                print(
                    f'{item.amount_account_currency:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.tag.value} \t {item.account.value} \t {item.description}'
                )
                tag = get_tag()
                desc = input("\tEnter description: ")
                response = input(f"Is item {user_input} correct? Type 'Y' to save or any character to discard.")
                desc = desc if desc not in ["", None] else item.description
                print(
                    f'{item.amount_account_currency:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {tag.value} \t {item.account.value} \t {desc}'
                )

                if response.lower() == "y":
                    item.tag = Tags(tag)
                    item.description = desc
                else:
                    print("Item discarded.")


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
                            item.bank_name,
                            item.account.value,
                            item.amount_account_currency,
                            item.account_currency,
                            item.amount_usd,
                            item.tag.name,
                            item.description,
                        ]
                    )


def check_for_duplicate_column_names(file_name, csv_reader: csv.DictReader) -> None:
    """Check for duplicate column names in the CSV file."""
    column_names = csv_reader.fieldnames
    duplicates = [column for column in set(column_names) if column_names.count(column) > 1]
    if duplicates:
        raise ValueError(f"Duplicate column names found: {duplicates} in file: {file_name}")


def get_exchange_rate(currency: str = "CZK", is_test: str = "Test Bank") -> float:
    """Check if the currency is in the exchange_usd_rate_history.log file and is not older than x days."""
    if currency == "USD":
        return 1.0

    days = 180 if is_test == "Test Bank" else 1
    try:
        with open("exchange_usd_rate_history.log", "r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[1] == currency:
                    date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                    if (datetime.now() - date).days < days:
                        return float(row[2])
    except FileNotFoundError:
        pass  # File does not exist, we will create it later

    # If the exchange rate is not found or is too old, fetch it from the API
    url = f"https://v6.exchangerate-api.com/v6/{CONFIG.exchangeRateApiKey}/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        exchange_rates = data.get("conversion_rates", {})
        rate = exchange_rates.get(currency)
        if rate is None:
            raise ValueError(f"Exchange rate for currency {currency} not found.")

        # Append new data to the file
        with open("exchange_usd_rate_history.log", "a", newline="") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), currency, rate])

        return float(rate)
    else:
        raise ValueError(f"Error: Unable to fetch data (status code: {response.status_code})")


def cleanup():
    # Perform cleanup operations here, e.g., closing files, releasing resources, etc.
    ALL_TRANSACTIONS.clear()


def signal_handler(sig, frame):
    print("\nCtrl+C detected. Cleaning up...")
    cleanup()
    sys.exit(0)
