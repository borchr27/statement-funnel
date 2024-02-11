from program.constants import ALL_TRANSACTIONS, CONFIG
import os
from program.utils import import_data
from datetime import datetime


class TestClass:
    def test_checking_transaction_import(self):
        """Test creating a checking transaction class from data."""
        directory = "./data/testing"
        file = open(f"{directory}/test.csv", "w")
        file.write(
            "Account Number,Transaction Date,Transaction Amount,Transaction Type,Transaction Description,Balance\n"
        )
        transactions = ["1234,08/25/23,-5.00,Debit,test,100.00\n", "1234,08/15/23,10.00,Credit,VENMO,810.20\n"]

        for t in transactions:
            file.write(t)
        file.close()
        import_data(directory)
        os.remove(f"{directory}/test.csv")

        for n, transaction in enumerate(transactions):
            s = transaction.replace("\n", "")  # string
            data = s.split(",")  # array
            t = ALL_TRANSACTIONS[0].transactions[n]
            assert t.date == datetime.strptime(data[1], "%m/%d/%y")
            assert t.bank == "Test Bank"
            assert t.account.value == "Savings"
            assert t.amount == float(data[2])
            assert t.description == data[4]

    def test_dotenv(self):
        """Test that the .env file is set up correctly."""
        assert isinstance(CONFIG["Accounts"][0]["Bank Name"], str)

    def test_format_data(self):
        assert True

    def test_review_data(self):
        assert True

    def test_insert_data(self):
        """Insert data into a file test."""
        assert True

    def test_main(self):
        assert True
