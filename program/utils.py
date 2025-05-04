import csv
import os
import sys
from datetime import datetime
from typing import List

import requests

from program.constants import CONFIG


def get_file_names(directory: str = "./data") -> List[str]:
    """Get names of files located in the first-level directory."""
    file_names = [
        file for file in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, file)) and file.endswith(".csv")
    ]
    # Remove "budget.csv" if present
    if "budget.csv" in file_names:
        file_names.remove("budget.csv")
    return file_names

# def format_and_tag_data_old() -> None:
#     """For each transaction in each account create a budget transaction item."""
#     for account in ALL_TRANSACTIONS.keys():
#         transactions = ALL_TRANSACTIONS[account].transactions
#         features = [f"{t.amount_account_currency} {t.description}" for t in transactions]
#         model = BertTextClassifier.load("private/saved_model")
#         assert len(transactions) == len(predictions), "Length mismatch between transactions and predictions."
#         for transaction, prediction in zip(transactions, predictions):
#             transaction.tag = Tags(prediction)
#             check_description(transaction)

def link(uri, label=None):
    if label is None:
        label = uri
    # OSC 8 ;; URI ST  label  OSC 8 ;; ST
    # where ST can be BEL (\a) or ESC backslash (\x1b\\). BEL is more widely supported.
    return f'\033]8;;{uri}\a{label}\033]8;;\a'

def show_paged_transactions(transactions: list, current_page=0) -> int:
    page_size = 15  # Number of items to show per page
    total_transactions = len(transactions)

    while current_page * page_size < total_transactions:
        start_index = current_page * page_size
        end_index = start_index + page_size
        for n, item in enumerate(transactions[start_index:end_index], start=start_index):
            item_description_link = f'https://www.google.com/search?q={item.description.replace(" ", "+")}'
            item_link = link(item_description_link)
            if item.tag:
                print(
                    f'{n} \t {item.amount_account_currency:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.bank_name} \t {item.account.value} \t {item.tag.name} \t {item.description} \t {item_link}'
                )
            else:
                print(
                    f'{n} \t {item.amount_account_currency:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.bank_name} \t {item.account.value} \t NULL \t {item_link}'
                )

        return current_page + 1


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



def signal_handler(sig, frame):
    print("\nCtrl+C detected. Cleaning up...")
    sys.exit(0)
