from program.constants import ALL_TRANSACTIONS, CONFIG
import os
import sys
from program.utils import import_data, format_data, review_data
from datetime import datetime
import pytest

WORK_DIR = "./data/testing"


# Fixture for setup tasks before each test method
@pytest.fixture(scope="function")
def setup_function():
    file = open(f"{WORK_DIR}/test.csv", "w")
    file.write(
        "Account Number,Transaction Date,Transaction Amount,Transaction Type,Transaction Description,Balance\n"
    )
    transactions = [
        "1234,08/25/23,-5.00,Debit,test,100.00\n",
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
        import_data(WORK_DIR)
        for n, transaction in enumerate(setup_function):
            s = transaction.replace("\n", "")  # string
            data = s.split(",")  # array
            t = ALL_TRANSACTIONS[0].transactions[n]
            assert t.date == datetime.strptime(data[1], "%m/%d/%y")
            assert t.bank == "Test Bank"
            assert t.account.value == "Savings"
            assert t.amount == float(data[2])
            assert t.description == data[4]

    def test_format_data(self, setup_function, monkeypatch):
        # Define an input value
        input_value = "m"  # stands for 'misc' tag

        # Use monkeypatch.setattr to replace the input() function
        # with a function that returns the custom input value
        monkeypatch.setattr("builtins.input", lambda _: input_value)
        # Redirect stdout to suppress output
        sys.stdout = open(os.devnull, "w")

        import_data(WORK_DIR)
        format_data()
        assert ALL_TRANSACTIONS[0].transactions[0].tag.value == "misc"
        assert ALL_TRANSACTIONS[0].transactions[1].tag.value == "misc"
        with pytest.raises(IndexError):
            var = ALL_TRANSACTIONS[0].transactions[2].tag.value

    def test_review_data(self, setup_function, monkeypatch):
        # Define an input value
        input_sequence = [
            "m",
            "m",
            "0",
            "f",
            "test_description",
            "y",
            "n",
            "",
        ]
        input_iterator = iter(input_sequence)  # Create an iterator

        def mock_input(prompt):
            return next(
                input_iterator
            )  # Use next() to fetch the next input, ignore prompt

        monkeypatch.setattr(
            "builtins.input", mock_input
        )  # Replace input with mock_input

        # Redirect stdout to suppress output
        sys.stdout = open(os.devnull, "w")
        # Use monkeypatch.setattr to replace the input() function
        # with a function that returns values from the input_sequence
        import_data(WORK_DIR)
        format_data()
        review_data()
        assert ALL_TRANSACTIONS[0].transactions[0].tag.value == "food"
        assert ALL_TRANSACTIONS[0].transactions[1].tag.value == "misc"
        with pytest.raises(IndexError):
            var = ALL_TRANSACTIONS[0].transactions[2].tag.value

    def test_dotenv(self):
        """Test that the .env file is set up correctly."""
        assert isinstance(CONFIG["accounts"][0]["bankName"], str)

    def test_insert_data(self):
        """Insert data into a file test."""
        assert True
