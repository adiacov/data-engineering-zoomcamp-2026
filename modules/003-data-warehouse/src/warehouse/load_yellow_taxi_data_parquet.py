import requests
from google.cloud import storage

import logging
from pathlib import Path

from common.config import get_root_path

logger = logging.getLogger(__name__)


def _download_file(file: Path) -> None:
    """Download yellow taxi dataset parquet file"""

    BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/{}"
    file_name = file.name

    logger.info("Downloading file conditionally %s", file_name)

    if not file.exists():
        logger.info("File does not exist locally. Downloading [%s]", file_name)

        url = BASE_URL.format(file_name)
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()

                with open(file, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

        except Exception as exc:
            logger.error(
                "Could not download file %s, because of error %s", file_name, exc
            )
            raise exc

        logger.info("Successfully downloaded file %s", file_name)


def _load_file_to_gcs(file: Path) -> None:

    BUCKET_NAME = "de_course_bucket"
    CHUNK_SIZE = 8 * 1024 * 1024

    # Create GCS client
    client = storage.Client()

    # Load file to bucket
    blob_name = "taxi/parquet/{}".format(file.name)
    logger.info("Loading file %s to GCS at %s", blob_name)

    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE
    blob.upload_from_filename(file)

    logger.info("Loaded file %s to GCS at %s", file.name, blob_name)


# NOTE: keep it simple for this module.
# don't complicate by providing year, month periods
# Normally, this would be a more robust function


def load_yellow_taxi_data_parquet():
    """Loads yellow taxi data parquet files to Google Cloud Storage"""

    logger.info("Loading taxi datasets to GCS...")

    FILE_NAME = "yellow_tripdata_2024-{}.parquet"
    DATA_DIR = get_root_path() / "data" / "taxi" / "parquet"

    # dataset month periods to load
    months = [f"{i:02d}" for i in range(2, 7)]

    # Download taxi data file, if it is missing locally
    for month in months:
        file_name = FILE_NAME.format(month)
        file = DATA_DIR / file_name

        _download_file(file)
        _load_file_to_gcs(file)

    logger.info("Loaded all datasets to GSC")
