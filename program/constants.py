from enum import Enum
import json

ALL_TRANSACTIONS = {}


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


class Config:
    def __init__(self, config_data):
        for key, value in config_data.items():
            setattr(self, key, value)


# Load the configuration file
with open('.env.json', 'r') as config_file:
    config_data = json.load(config_file)

# Create a Config instance
CONFIG = Config(config_data)

ids = set()
for n in range(len(CONFIG.accounts)):
    ids.add(CONFIG.accounts[n]['id'])
