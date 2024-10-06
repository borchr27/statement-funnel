from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, List, Optional
from program.constants import Account, Tags


T = TypeVar("T")

# date,bank,account,amount_account_currency,tag,description,amount_usd,account_currency


@dataclass
class Transaction:
    account: Account
    account_currency: str
    amount_account_currency: float
    amount_usd: float
    bank_name: str
    date: datetime
    description: str
    tag: Optional[Tags] = None

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
