import os
from dotenv import load_dotenv
from enum import Enum, auto
import json

load_dotenv()

CONFIG = json.loads(os.environ.get("CONFIG"))
ALL_TRANSACTIONS = {}

ids = set()
for config in CONFIG["Accounts"]:
    id = config["Id"]
    if id in ids:
        raise ValueError(f"Duplicate id: {id}")
    ids.add(id)


class Account(Enum):
    CREDIT_CARD = "Credit Card"
    SAVINGS = "Savings"
    CHECKING = "Checking"


class Tag(Enum):
    FOOD = "food"
    MISC = "misc"
    RENT = "rent"
    PAY = "pay"
    GAS = "gas"
    OUT = "out"
