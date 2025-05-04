import os
from enum import Enum
import json

CONFIG_FILE = os.getenv("ENV")


class Account(Enum):
    CREDIT_CARD = "Credit Card"
    SAVINGS = "Savings"
    CHECKING = "Checking"


class Tags(Enum):
    misc = 0
    pay = 1
    out = 2
    gas = 3
    food = 4
    rent = 5

N_CLASSES = len(Tags)
N_NUMERICAL_FEATURES = 4 # Year, Month, Day, Amount
# MODEL_SAVE_DIRECTORY = os.path.join(os.getcwd(), "private/saved_model")
user = os.getenv("USER")
SECRETS_DIR = f"/home/{user}/secrets/statement-funnel"
MODEL_SAVE_DIRECTORY = f"{SECRETS_DIR}/private/saved_model"
NUMERIC_COLUMNS = ['amount_usd', 'year', 'month', 'day']
TEXT_COLUMNS = [i for i in range(768)]  # Generates ["0", ..., "767"]

class Config:
    def __init__(self, config_data):
        for key, value in config_data.items():
            setattr(self, key, value)

CONFIG_FILE = f"{SECRETS_DIR}/.env.json"
# Load the configuration file
with open(CONFIG_FILE, "r") as config_file:
    config_data = json.load(config_file)

# Create a Config instance
CONFIG = Config(config_data)
