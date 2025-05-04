import os

from program.collection_class import Collection

os.environ["ENV"] = ".env_test.json"

import sys
import pytest
from datetime import datetime
from program.constants import CONFIG
from program.utils import get_exchange_rate

WORK_DIR = "./data/testing"


# Fixture for setup tasks before each test method
@pytest.fixture(scope="function")
def setup_function():
    file = open(f"{WORK_DIR}/test.csv", "w")
    file.write("Account Number,Transaction Date,Transaction Amount,Transaction Type,Transaction Description,Balance\n")
    transactions = [
        "1234,08/25/23,5.00,Debit,test,100.00\n",
        "1234,08/15/23,10.00,Credit,VENMO,810.20\n",
    ]

    for t in transactions:
        file.write(t)
    file.close()
    yield transactions

    # Cleanup code goes here
    os.remove(f"{WORK_DIR}/test.csv")


class TestClass:
    def test_import(self, setup_function):
        """Test creating a checking transaction class from data."""
        collection = Collection()
        collection.import_data(WORK_DIR)
        for n, transaction in enumerate(setup_function):
            s = transaction.replace("\n", "")  # string
            data = s.split(",")  # array
            t = collection.transactions[n]
            amount = -float(data[2]) if data[3] == "Debit" else float(data[2])
            assert t.date == datetime.strptime(data[1], "%m/%d/%y")
            assert t.bank_name == "Test Bank"
            assert t.account.value == "Savings"
            assert t.amount_account_currency == amount
            assert t.description == data[4]

    def test_format_data(self, setup_function, monkeypatch):
        # Define an input value
        input_value = "m"  # stands for 'misc' tag

        # Use monkeypatch.setattr to replace the input() function
        # with a function that returns the custom input value
        monkeypatch.setattr("builtins.input", lambda _: input_value)
        # Redirect stdout to suppress output
        sys.stdout = open(os.devnull, "w")
        collection = Collection()
        collection.import_data(WORK_DIR)
        collection.format_and_tag_data()
        assert collection.transactions[0].tag.name == "misc"
        assert collection.transactions[1].tag.name == "out"
        with pytest.raises(IndexError):
            var = collection.transactions[2].tag.name

    def test_review_data(self, setup_function, monkeypatch):
        # Define an input value
        input_sequence = [
            "0",
            "f",
            "",
            "y",
            "1",
            "m",
            "test_description",
            "y",
            "q",
        ]
        input_iterator = iter(input_sequence)  # Create an iterator

        def mock_input(prompt):
            return next(input_iterator)  # Use next() to fetch the next input, ignore prompt

        monkeypatch.setattr("builtins.input", mock_input)  # Replace input with mock_input

        # Redirect stdout to suppress output
        sys.stdout = open(os.devnull, "w")
        # Use monkeypatch.setattr to replace the input() function
        # with a function that returns values from the input_sequence
        collection = Collection()
        collection.import_data(WORK_DIR)
        collection.format_and_tag_data()
        collection.review_data()
        assert collection.transactions[0].tag.name == "food"
        assert collection.transactions[1].tag.name == "misc"
        with pytest.raises(IndexError):
            var = collection.transactions[2].tag.name

    def test_env_file(self):
        """Test that the .env.json file is set up correctly."""
        assert isinstance(CONFIG.accounts[0]["bankName"], str)

    def test_get_exchange_rates(self):
        """Test that the exchange rates are fetched correctly."""
        if CONFIG.exchangeRateApiKey != "":
            currency_code = CONFIG.accounts[0]["ormInformation"]["currencyCode"]
            assert currency_code == "EUR"
            assert isinstance(get_exchange_rate(currency_code), float)
