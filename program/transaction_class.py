from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, List, Optional

import pandas as pd

from program.constants import Account, Tags

T = TypeVar("T")

# date,bank,account,amount_account_currency,tag,description,amount_usd,account_currency


@dataclass
class Transaction:
    _instance = None
    account: Account
    account_id: int
    account_currency: str
    amount_account_currency: float
    amount_usd: float
    bank_name: str
    date: datetime
    description: str
    origin_file_name: str
    tag: Optional[Tags] = None

    def __post_init__(self):
        if isinstance(self.account, str):
            try:
                self.account = Account[self.account.upper()]  # Convert to uppercase for case-insensitive matching
            except KeyError:
                raise ValueError(f"No matching enum value for account: {self.account}")

    def to_dict(self):
        """Convert a Transaction instance to a dictionary"""
        return {
            "account": self.account.name if isinstance(self.account, Account) else self.account,
            "account_currency": self.account_currency,
            "amount_account_currency": self.amount_account_currency,
            "amount_usd": self.amount_usd,
            "bank_name": self.bank_name,
            "date": self.date,
            "description": self.description,
            "tag": self.tag.name if self.tag else None,
        }

    @staticmethod
    def to_dataframe(transactions: List["Transaction"]) -> pd.DataFrame:
        """Convert a list of Transaction objects into a Pandas DataFrame"""
        return pd.DataFrame([t.to_dict() for t in transactions])

