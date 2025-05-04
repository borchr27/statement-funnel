import os

from program.collection_class import Collection
from program.constants import SECRETS_DIR

os.environ["ENV"] = ".env.json"

import signal
from program.utils import (
    signal_handler,
)

# Register the Ctrl+C (SIGINT) signal handler
signal.signal(signal.SIGINT, signal_handler)


def main():
    # for testing
    # working_directory = "./data/examples/"
    collection = Collection()
    working_directory = f"{SECRETS_DIR}/private/"
    collection.import_data(working_directory)
    collection.format_and_tag_data()
    collection.review_data()
    collection.insert_data_to_file(working_directory)



if __name__ == "__main__":
    main()
    # TODO retrain model
    # TODO add category into description for one dataset
    # TODO add sorting at end of adding data
    # TODO fix failing test that manually inputs / changes data
