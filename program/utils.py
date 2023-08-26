import csv
import os
from typing import List
from datetime import datetime
from typing import List
from program.transaction_class import Transactions, DebitTransaction, CreditCardTransaction
from program.budget_class import Tag
from program.constants import ACC_DEBIT, ACC_CREDITCARD, BUDGET_ITEMS
from program.helper_functions import debit_convert, credit_convert, get_tag, print_warning_message

ACC_DEBIT = Transactions(transactions=[], origin_file_name="")
ACC_CREDITCARD = Transactions(transactions=[], origin_file_name="")
BUDGET_ITEMS = []

def get_file_names() -> List[str]:
	"""Get name of files located in the /data directory."""
	directory = './data'
	file_names = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file)) and '.csv' in file]
	file_names.remove('budget.csv')
	return file_names

def import_data(file_names: List[str]) -> None:
	""""Import data from .csv files exported from bank website into defined classes."""
	for file_name in file_names:
		if 'Checking' in file_name:
			current_account = ACC_DEBIT
		else:
			current_account = ACC_CREDITCARD
		current_account.origin_file_name = file_name

		with open(f'./data/{file_name}', 'r') as file:
			csv_reader = csv.DictReader(file)

			for row in csv_reader:
				if 'Checking' in file_name:
					description = row['Transaction Description']
					trans_date = datetime.strptime(row['Transaction Date'], '%m/%d/%y')
					account_number = int(row['Account Number'])
					amt = float(row['Transaction Amount'])
					trans_type = row['Transaction Type']
					balance = float(row['Balance'])
					current_account.transactions.append(DebitTransaction(trans_date=trans_date, description=description, account_number=account_number, amount=amt, transaction_type=trans_type, balance=balance))
				else:
					description = row['Description']
					trans_date = datetime.strptime(row['Transaction Date'], '%Y-%m-%d')
					posted_date = datetime.strptime(row['Posted Date'], '%Y-%m-%d')
					card_num = int(row['Card No.'])
					category = row['Category']
					debit = float(row['Debit']) if row['Debit'] else 0.0
					credit = float(row['Credit']) if row['Credit'] else 0.0
					current_account.transactions.append(CreditCardTransaction(posted_date=posted_date, card_num=card_num, category=category, debit=debit, credit=credit, description=description, trans_date=trans_date))


def format_data() -> None:
	"""For each transaction in each account create a budget transaction item."""
	for account in [ACC_DEBIT, ACC_CREDITCARD]:
		for transaction in account.transactions:
			if isinstance(transaction, DebitTransaction):
				budget_item = debit_convert(transaction)
			elif isinstance(transaction, CreditCardTransaction):
				budget_item = credit_convert(transaction)
			else:
				raise TypeError(f'Unknown transaction type: {type(transaction)}')
			
			if budget_item:
				BUDGET_ITEMS.append(budget_item)
			

def review_data() -> None:
	"""Display the budget items to the user for review and allow them to edit the items."""
	for n, item in enumerate(BUDGET_ITEMS):
		print(f'{n} \t {item.cost:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.tag.value} \t {item.account.value} \t {item.description}')
	while True:
		item_number = input('Enter item number to edit (enter to continue): ')
		if item_number in ['', None]:
			break
		else:
			try:
				item_number = int(item_number)
			except ValueError:
				print_warning_message('Invalid input. Please enter a number.')
				continue
			item = BUDGET_ITEMS[item_number]
			print(f'{item.cost:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {item.tag.value} \t {item.account.value} \t {item.description}')
			tag = get_tag()
			desc = input('\tEnter description: ')
			print(f"Is item {item_number} correct? Type 'Y' to save or any character to discard.")
			print(f'{item.cost:10.2f} \t\t {item.date.strftime("%m/%d/%y")} \t {tag.value} \t {item.account.value} \t {desc}')
			response = input('Response: ')

			if response.lower() == 'y':
				item.tag = Tag(tag)
				item.description = desc
			else:
				print('Item discarded.')

def insert_data_to_file() -> None:
	"""Insert budget items into budget.csv file."""
	# TODO: check if item exists, if not create it
	for item in BUDGET_ITEMS:
		with open('./data/budget.csv', 'a') as file:
			csv_writer = csv.writer(file)
			csv_writer.writerow([item.date.strftime('%m/%d/%y'), item.cost, item.tag.value, item.description, item.account.value])

def insert_data_to_db() -> None:
	"""Insert budget items into a database."""
	pass