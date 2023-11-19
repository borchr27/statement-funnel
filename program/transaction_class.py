from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, List, Optional
from program.constants import Account, Tag


T = TypeVar("T")


@dataclass
class Transaction:
    amount: float
    bank: str
    currency: str
    date: datetime
    description: str
    account: Account
    tag: Optional[Tag] = None

    def __post_init__(self):
        if isinstance(self.account, str):
            try:
                self.account = Account[self.account.upper()]  # Convert to uppercase for case-insensitive matching
            except KeyError:
                raise ValueError(f"No matching enum value for account: {self.account}")


@dataclass
class AccountInformation:
    origin_file_name: str
    transactions: List[Transaction]
