from warehouse.load_yellow_taxi_data_parquet import load_yellow_taxi_data_parquet
from warehouse.load_yellow_taxi_data_csv import stream_csv_gz_url_to_gcs

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

        # Loads yellow taxi data parquet files to Google Cloud Storage
        # load_yellow_taxi_data_parquet()

        # Loads as a stream, a .csv.gz file from URL directly to GCS bucket
        month = "03"  # which month do download the yellow trip data 2019
        stream_csv_gz_url_to_gcs(
            url=f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-{month}.csv.gz",
            bucket_name="de_course_bucket",
            blob_name=f"taxi/yellow_tripdata_2019-{month}.csv",
        )

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
