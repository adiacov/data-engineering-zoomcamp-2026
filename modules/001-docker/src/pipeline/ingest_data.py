import pandas as pd
from pandas.io.parsers.readers import TextFileReader
from sqlalchemy import create_engine, Engine
import click
from tqdm.auto import tqdm
import requests
from requests import HTTPError

import os
from pathlib import Path
from typing import Literal

from common.config import get_root_path

# In a real application, this and other settings should be provided via environment variables
_DB_HOST = os.getenv("DB_HOST", "localhost")
_ROOT_PATH = get_root_path()

# resolve local vs docker path to /data folder
_DATA_PATH = Path(os.getenv("DATA_DIR", _ROOT_PATH / "data"))
_METADATA_PATH = _DATA_PATH / "ingestion-metadata.csv"

# Ensure data directory exists
_DATA_PATH.mkdir(parents=True, exist_ok=True)

_DATASET_TYPES = ["yellow-taxi", "taxi-zones"]
DatasetType = Literal["yellow-taxi", "taxi-zones"]

_YELLOW_TAXI_DATA_SCHEMA = {
    "VendorID": "Int64",
    "tpep_pickup_datetime": "string",
    "tpep_dropoff_datetime": "string",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
}

_YELLOW_TAXI_DATE_COLUMNS = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]

_TAXI_ZONES_DATA_SCHEMA = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string",
}
_TAXI_ZONES_DATE_COLUMNS = None


def download_dataset(url: str, target: Path) -> None:
    """Download a dataset from the internet and save it to disk."""
    print(f"[INFO] Downloading data from {url} to {target}")
    try:
        with requests.get(url=url, allow_redirects=True, stream=True) as r:
            r.raise_for_status()
            with open(target, "wb") as file:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    file.write(chunk)
        print("[INFO] Download completed successfully")
    except HTTPError as exc:
        print(f"[ERROR] Download failed: {exc}")
        raise


def get_dataset_iterator(
    file_path: Path, chunk_size: int, dataset_type: DatasetType
) -> TextFileReader:
    """Create a pandas CSV iterator for the given dataset file."""
    if dataset_type == "yellow-taxi":
        schema = _YELLOW_TAXI_DATA_SCHEMA
        date_cols = _YELLOW_TAXI_DATE_COLUMNS
    else:
        schema = _TAXI_ZONES_DATA_SCHEMA
        date_cols = _TAXI_ZONES_DATE_COLUMNS

    return pd.read_csv(
        file_path,
        dtype=schema,
        parse_dates=date_cols,
        iterator=True,
        chunksize=chunk_size,
    )


def load_dataset(engine: Engine, df_iterator: TextFileReader, table_name: str) -> None:
    """Load a dataset into the database in chunks."""
    is_first = True
    total_inserted = 0

    print(f"[INFO] Loading data into database table '{table_name}'")

    for chunk in tqdm(df_iterator, "Ingestion progress"):
        if is_first:
            chunk.head(0).to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
            )
            is_first = False
            print(f"\n[INFO] Table '{table_name}' created")

        chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",
        )

        total_inserted += len(chunk)
        print(f"[INFO] Inserted {len(chunk)} rows (total: {total_inserted})")

    print(f"[INFO] Data successfully loaded into table '{table_name}'")


def read_metadata() -> pd.DataFrame:
    """Read ingestion metadata from disk."""
    print("[INFO] Reading ingestion metadata")
    if not _METADATA_PATH.exists():
        return pd.DataFrame(columns=["source", "file_size"])
    return pd.read_csv(
        _METADATA_PATH, dtype={"source": "string", "file_size": "string"}
    )


def write_metadata(file_path: Path, file_size: str | None) -> None:
    """Store or update metadata for an ingested dataset."""
    df = read_metadata()
    source = file_path.name

    if source in df["source"].values:
        df.loc[df["source"] == source, "file_size"] = file_size
    else:
        df.loc[len(df)] = {"source": source, "file_size": file_size}

    df.to_csv(_METADATA_PATH, index=False)
    print(f"[INFO] Metadata updated for '{source}'")


def get_dataset_size(url: str) -> str | None:
    """Retrieve dataset size from the HTTP Content-Length header."""
    print(f"[INFO] Retrieving dataset size from {url}")
    try:
        with requests.get(
            url, stream=True, headers={"Accept-Encoding": "identity"}
        ) as r:
            r.raise_for_status()
            return r.headers.get("Content-Length")
    except HTTPError:
        print(f"[WARNING] Content-Length header not available for {url}")
        return None


def check_dataset_type(name: DatasetType) -> None:
    if name not in _DATASET_TYPES:
        raise ValueError(f"Unsupported dataset type '{name}'")


def ingest_data(
    engine: Engine,
    dataset_url: str,
    table_name: str,
    chunk_size: int,
    dataset_type: DatasetType,
) -> None:
    """Ingest a dataset file if missing or changed."""
    print(f"[INFO] Starting ingestion for dataset type '{dataset_type}'")
    check_dataset_type(dataset_type)

    file_name = dataset_url.split("/")[-1]
    file_path = _DATA_PATH / file_name

    metadata = read_metadata()
    local_size = (
        metadata.loc[metadata["source"] == file_name, "file_size"].squeeze()
        if not metadata.empty
        else None
    )

    web_size = get_dataset_size(dataset_url)

    should_reload = not file_path.exists() or web_size is None or web_size != local_size

    if should_reload:
        print("[INFO] Downloading and loading dataset")
        download_dataset(dataset_url, file_path)

        df_iter = get_dataset_iterator(file_path, chunk_size, dataset_type)
        load_dataset(engine, df_iter, table_name)

        write_metadata(file_path, web_size)
    else:
        print("[INFO] Local dataset is up to date")

    print(f"[INFO] Ingestion completed for dataset type '{dataset_type}'")


@click.command()
@click.option("--year", default=2021, show_default=True)
@click.option("--month", default=1, show_default=True)
@click.option("--chunksize", default=100000, show_default=True)
@click.option("--db-user", default="postgres", show_default=True)
@click.option("--db-password", default="postgres", show_default=True)
@click.option("--db-name", default="ny_taxi", show_default=True)
@click.option("--db-table-prefix", default="yellow_taxi_data", show_default=True)
def run(year, month, chunksize, db_user, db_password, db_name, db_table_prefix):
    """Run the data ingestion pipeline."""
    print("[INFO] Starting taxi data ingestion pipeline")

    db_table = f"{db_table_prefix}_{year}_{month:02d}"

    yellow_url = (
        "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/"
        f"yellow_tripdata_{year}-{month:02d}.csv.gz"
    )
    zones_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

    engine = create_engine(
        f"postgresql://{db_user}:{db_password}@{_DB_HOST}:5432/{db_name}"
    )

    ingest_data(engine, yellow_url, db_table, chunksize, "yellow-taxi")
    ingest_data(engine, zones_url, "taxi_zones_lookup", 100, "taxi-zones")

    print("[INFO] Taxi data ingestion completed successfully")


if __name__ == "__main__":
    run()
