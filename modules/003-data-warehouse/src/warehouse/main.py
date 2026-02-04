from warehouse.load_yellow_taxi_data import load_yellow_taxi_data

from dotenv import load_dotenv
import logging

from common.config import set_logging

set_logging()
logger = logging.getLogger(__name__)
load_dotenv(".env.warehouse")


def main():
    """App entry point for warehouse module 3.

    NOTE:
    Be careful. Run it only if you truly need to load files.
    It consumes internet traffic.

    To allow file loading, set ALLOW_LOADING=True
    """

    ALLOW_LOADING = False
    if ALLOW_LOADING:
        logger.warning(
            "You are sure about this. It will load many many bytes of data from internet to Google Cloud Storage"
        )
        logger.info("Start loading data to GCS...")

        load_yellow_taxi_data()

        logger.info("Finished loading data to Google Cloud Storage")
    else:
        logger.warning(
            "It seams like you are trying to load data to Google Cloud Storage."
        )
        logger.info(
            "If you are sure of what you are about to do, enable loading by setting ALLOW_LOADING to True, in the main.py"
        )


if __name__ == "__main__":
    main()
