import requests
import gzip
from google.cloud import storage

import logging

logger = logging.getLogger(__name__)

def stream_csv_gz_url_to_gcs(url: str, bucket_name: str, blob_name: str):
    """Loads yellow taxi data CSV files to Google Cloud Storage"""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    logger.info("Uploading CSV file %s to GS bucket %s", blob_name, bucket_name)
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        # Stream decompress
        with gzip.GzipFile(fileobj=r.raw) as gz:
            # Stream upload to GCS
            with blob.open("wb") as f:
                while True:
                    chunk = gz.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    f.write(chunk)
                    
    logger.info("Uploaded CSV file %s to GS bucket %s", blob_name, bucket_name)

