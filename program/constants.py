import os
from dotenv import load_dotenv
from enum import Enum, auto
import json

load_dotenv()

CONFIG = json.loads(os.environ.get("CONFIG"))
ALL_TRANSACTIONS = {}

ids = set()
for config in CONFIG["accounts"]:
    id = config["id"]
    if id in ids:
        raise ValueError(f"Duplicate id: {id}")
    ids.add(id)


class Account(Enum):
    CREDIT_CARD = "Credit Card"
    SAVINGS = "Savings"
    CHECKING = "Checking"



class NewTag(Enum):
    misc = 0
    pay = 1
    out = 2
    gas = 3
    food = 4
    rent = 5
