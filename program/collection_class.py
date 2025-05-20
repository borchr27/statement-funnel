import csv
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import pandas as pd
from sympy.printing.pytorch import torch

from ai.bert_embedding_model import BertEmbeddings
from ai.data_loader import preprocess_historical_data
from ai.neural_network_model import MultimodalTrainer, MultimodalModel
from program.constants import CONFIG, Tags, NUMERIC_COLUMNS, TEXT_COLUMNS, MODEL_SAVE_DIRECTORY, SECRETS_DIR
from program.helper_functions import print_warning_message, check_description, get_tag
from program.transaction_class import Transaction
from program.utils import get_exchange_rate, get_file_names, check_for_duplicate_column_names, show_paged_transactions


@dataclass
class Collection:
    _instance = None
    transactions: List[Transaction] = field(default_factory=list)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Collection()
        return cls._instance

    def to_dataframe(self) -> pd.DataFrame:
        """Convert a list of Transaction objects into a Pandas DataFrame"""
        return pd.DataFrame([t.to_dict() for t in self.transactions])

    def import_data(self, directory: str) -> None:
        """Import data from .csv files exported from bank website into defined classes."""
        file_names = get_file_names(directory)
        for file_name in file_names:
            account_id = None
            for config in CONFIG.accounts:
                if config["keyword"] in file_name:
                    account_id = config["id"]
                    break
            assert account_id is not None, f"No account id found for file: {file_name}"
            ap = CONFIG.accounts[account_id]["ormInformation"]  # account prefix

            with open(f"{directory}/{file_name}", "r", encoding="UTF-8", errors="replace") as file:
                delimiter = ap["delimiter"]
                csv_reader = csv.DictReader(file, delimiter=delimiter)

                check_for_duplicate_column_names(file_name, csv_reader)

                for row in csv_reader:
                    try:
                        date = datetime.strptime(row[ap["date"]], ap["dateFormat"])
                        currency_code = ap["currencyCode"] if ap["currencyCode"] not in [""] else row["Currency"]
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
                        elif row[ap["transactionType"]] in ["EXCHANGE", "TOPUP"]: # For account id 4
                            if float(row["Fee"]) == 0.0:
                                continue
                            amount = float(row["Fee"])
                        else:
                            amount = float(row[ap["amount"]].replace(",", ".").replace(" ", ""))

                    except ValueError:
                        print_warning_message(f"Error parsing row: {row} in file: {file_name}.")

                    self.transactions.append(
                        Transaction(
                            description=description,
                            date=date,
                            amount_account_currency=amount,
                            account_currency=currency_code,
                            bank_name=bank,
                            account=account_name,
                            amount_usd=round(amount / get_exchange_rate(currency_code, is_test=bank), 2),
                            origin_file_name=file_name,
                            account_id=account_id,
                        )
                    )
        return


    def format_and_tag_data(self) -> None:
        """For each transaction in each account create a budget transaction item."""
        processed_data = preprocess_historical_data(self.to_dataframe(), True)
        numeric_tensor = torch.Tensor(processed_data[NUMERIC_COLUMNS].values)
        text_tensor = torch.Tensor(processed_data[TEXT_COLUMNS].values)
        trainer = MultimodalTrainer.load(MultimodalModel, MODEL_SAVE_DIRECTORY + "/saved_model.pth")
        predictions = trainer.predict(numeric_tensor, text_tensor).tolist()
        assert len(self.transactions) == len(predictions), "Length mismatch between transactions and predictions."
        for t, p in zip(self.transactions, predictions):
            t.tag = Tags(p)
            check_description(t)

    def review_data(self) -> None:
        """Display the budget items to the user for review and allow them to edit the items."""
        transactions = self.transactions
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
                except IndexError:
                    print_warning_message("Invalid input. Please enter a value within the range of current items.")
                    continue
                except AttributeError:
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

    def insert_data_to_file(self, directory: str) -> None:
        """Insert budget items into budget.csv file."""

        budget_items = self.transactions
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