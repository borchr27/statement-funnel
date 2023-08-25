from dataclasses import dataclass
from enum import Enum

class Account(Enum):
    CREDITCARD = "CC"
    CHECKING = "D"

class Tag(Enum):
    FOOD = "food"
    MISC = "misc"
    RENT = "rent"
    PAY = "pay"
    GAS = "gas"
    OUT = "out"

@dataclass
class BudgetRecord:
    """A budget item is inserted into the budget .csv file."""
    date: str
    cost: float
    tag: Tag
    description: str
    account: Account
