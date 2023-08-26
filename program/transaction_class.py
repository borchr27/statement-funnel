from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, List
from enum import Enum, auto

T = TypeVar("T")

class TransactionType(Enum):
	DEBIT = "Debit"
	CREDIT = "Credit"

	@classmethod
	def from_string(cls, value):
		if value.lower() == "debit":
			return cls.DEBIT
		elif value.lower() == "credit":
			return cls.CREDIT
		else:
			raise ValueError(f"Unknown transaction type: {value}")

@dataclass
class Transactions:
	transactions: List[T]
	origin_file_name: str

@dataclass
class Transaction:
	transaction_date: datetime
	description: str

@dataclass
class DebitTransaction(Transaction):
	account_number: int
	amount: float
	transaction_type: TransactionType
	balance: float 

	def __post_init__(self):
		if isinstance(self.transaction_type, str):
			self.transaction_type = TransactionType.from_string(self.transaction_type)


@dataclass
class CreditCardTransaction(Transaction):
	posted_date: datetime
	card_num: int
	category: str
	debit: float
	credit: float