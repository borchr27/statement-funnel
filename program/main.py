import os

os.environ["ENV"] = ".env.json"

import signal
from program.utils import (
    import_data,
    format_and_tag_data,
    review_data,
    insert_data_to_file,
    signal_handler,
)

# Register the Ctrl+C (SIGINT) signal handler
signal.signal(signal.SIGINT, signal_handler)


def main():
    # for testing
    # working_directory = "./data/examples/"
    working_directory = "./private/"
    import_data(working_directory)
    format_and_tag_data()
    review_data()
    insert_data_to_file(working_directory)



if __name__ == "__main__":
    main()
    # TODO retrain model
    # TODO add category into description for one dataset
    # TODO add sorting at end of adding data
    # TODO fix failing test that manually inputs / changes data
