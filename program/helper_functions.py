from program.transaction_class import DebitTransaction, CreditCardTransaction
from program.budget_class import BudgetRecord, Account, Tag
from typing import TypeVar, List
from program.constants import BANK_NAME

T = TypeVar("T")

def debit_convert(t: DebitTransaction) -> BudgetRecord:
	"""Mainly want to handle venmo and atm withdrawls from this account. Review and label transactions manually."""
	account = Account.CHECKING
	description = t.description
	amount = get_amount(t)
	if 'ATM ' in description:
		return BudgetRecord(cost=amount, date=t.transaction_date, description='cash', account=account, tag=Tag.MISC)
	elif ' VENMO ' in description:
		print(f"{t.transaction_date.strftime('%m/%d/%y')} -- {t.amount} -- {description}")
		desc_info = input('\tEnter VENMO description: ')
		description = desc_info if desc_info not in ['', None] else description
		return BudgetRecord(cost=amount, date=t.transaction_date, description=description, account=account, tag=Tag.MISC, )
	else:
		print(f"{t.transaction_date.strftime('%m/%d/%y')} -- {t.amount} -- {description}")
		desc_info = input('\tAdd description (click Enter to skip): ')
		if desc_info not in ['', None]:
			tag = determine_tag(t)
			return BudgetRecord(date=t.transaction_date, cost=amount, description=desc_info, tag=tag, account=account)
	return None

def get_amount(t: T) -> float:
	"""Get amount from credit cart transaction with correct sign."""
	if isinstance(t, DebitTransaction):
		return t.amount
	elif isinstance(t, CreditCardTransaction):
		return -t.credit if t.credit != 0.0 else t.debit
	else:
		raise TypeError(f"Invalid type: {type(t)}")
	
def credit_convert(t: CreditCardTransaction) -> BudgetRecord:
	account = Account.CREDITCARD
	bank_name = BANK_NAME #ignore payments that have BANK NAME, (case specific)
	description = t.description
	if bank_name not in description:
		amount = get_amount(t)
		updated_desc = 'RETURN ' + description if t.credit != 0.0 else description
		tag = determine_tag(t)  #eventually do this with machine learning
		return BudgetRecord(date=t.posted_date, cost=amount, tag=tag, description=updated_desc, account=account)
	return BudgetRecord

def determine_tag(t: T) -> Tag:
	"""Find tag for transaction based on description."""
	if not isinstance(t, DebitTransaction): # other wise we show the info twice
		print(f"{t.transaction_date.strftime('%m/%d/%y')} -- {get_amount(t)} -- {t.description}")
	return get_tag()

def get_tag() -> Tag:
	"""Get tag from the user."""
	while True:
		value = input('\tEnter tag: ')
		for tag in Tag:
			if value in tag.value and value not in [None, '']:
				return tag
		else:
			print_warning_message('Invalid tag, try again.')
			

def print_warning_message(message: str) -> None:
	"""Display warning message in red to the user."""
	print('\033[31m', end='')
	print(f'WARNING: {message}')
	print('\033[0m', end='')