import program.main as main
import os
from program.utils import import_data
from datetime import datetime

class TestClass:
	def test_debit_transaction_import(self):
		"""Test creating a debit transaction class from data."""
		file = open("data/Checking_test.csv", "w")
		file.write("Account Number,Transaction Date,Transaction Amount,Transaction Type,Transaction Description,Balance\n")
		transactions = ["1234,08/25/23,-5.00,Debit,test,100.00\n", "1234,08/15/23,10.00,Credit,VENMO,810.20\n"]
		
		for t in transactions:
			file.write(t)
		file.close()
		import_data(["Checking_test.csv"])
		os.remove("data/Checking_test.csv")

		for n, transaction in enumerate(transactions):
			s = transaction.replace("\n", "") # string
			data = s.split(",")	# array
			t = main.ACC_DEBIT.transactions[n]  # transaction
			assert t.account_number == int(data[0])
			assert t.transaction_date == datetime.strptime(data[1], '%m/%d/%y')
			assert t.amount == float(data[2])
			assert t.transaction_type.value == data[3]
			assert t.description == data[4]
			assert t.balance == float(data[5])

	def test_format_data(self):
		assert True

	def test_review_data(self):
		assert True

	def test_insert_data(self):
		"""Insert data into a file test."""
		assert True

	def test_main(self):
		assert True