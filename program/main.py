import signal
import sys
from program.utils import (
    import_data,
    format_and_tag_data,
    review_data,
    insert_data_to_file,
    signal_handler,
    cleanup,
)

# Register the Ctrl+C (SIGINT) signal handler
signal.signal(signal.SIGINT, signal_handler)


def main():
    try:
        working_directory = "./data/examples/"
        import_data(working_directory)
        format_and_tag_data()
        review_data()
        insert_data_to_file(working_directory)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
