from program.transaction_class import Transaction
from program.transaction_class import Tag
from typing import TypeVar
from program.constants import CONFIG

T = TypeVar("T")


def check_descriptions(t: Transaction):
    """Mainly want to handle venmo and atm withdrawals and review/label transactions manually."""
    description = t.description
    if "ATM " in description:
        t.description = "cash"
        t.tag = Tag.MISC
        return

    if " VENMO " in description:
        t.tag = determine_tag(t)
        desc_info = input("\tEnter VENMO description: ")
        t.description = f"VENMO: {desc_info}"
        return

    keywords = CONFIG["globalKeywords"]
    for keyword in keywords:
        if keyword in description:
            return

    t.tag = determine_tag(t)
    if description in ["", None]:
        desc_info = input("\tAdd description (click Enter to skip): ")
        t.description = desc_info
    return


def determine_tag(t: Transaction) -> Tag:
    """Find tag for transaction based on description."""
    print(f"{t.date.strftime('%m/%d/%y')} -- {t.amount} -- {t.description}")
    return get_tag()


def get_tag() -> Tag:
    """Get tag from the user. User only needs to enter first letter."""
    tag_dict = {tag.value[0]: tag for tag in Tag}
    while True:
        user_tag = input("\tEnter tag: ")
        if user_tag in tag_dict.keys() and user_tag not in [None, ""]:
            return tag_dict[user_tag]
        else:
            print_warning_message("Invalid tag, try again.")


def print_warning_message(message: str) -> None:
    """Display warning message in red to the user."""
    print("\033[31m", end="")
    print(f"WARNING: {message}")
    print("\033[0m", end="")


def print_info_message(message: str) -> None:
    """Display warning message in yellow to the user."""
    print("\033[33m", end="")
    print(f"{message}")
    print("\033[0m", end="")
