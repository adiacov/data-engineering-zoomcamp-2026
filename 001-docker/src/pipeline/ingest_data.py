import pandas as pd
from sqlalchemy import create_engine
import click
from tqdm.auto import tqdm
import os


# Normally this env and many others in this app will be transmitted with env vars
_DB_HOST = os.getenv("DB_HOST", "localhost")

_DATA_SCHEMA = {
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

_DATE_COLUMNS = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]


@click.command()
@click.option("--year", default=2021, show_default=True, help="Year of the dataset")
@click.option("--month", default=1, show_default=True, help="Month of the dataset")
@click.option(
    "--chunksize", default=100000, show_default=True, help="Number of rows per chunk"
)
@click.option("--db-user", default="postgres", show_default=True, help="Database user")
@click.option(
    "--db-password", default="postgres", show_default=True, help="Database password"
)
@click.option("--db-name", default="ny_taxi", show_default=True, help="Database name")
@click.option(
    "--db-table",
    default="yellow_taxi_data",
    show_default=True,
    help="Target database table",
)
def run(year, month, chunksize, db_user, db_password, db_name, db_table):
    """Run the ETL pipeline"""
    click.echo(f"Running ETL for {year}-{month:02d}")
    click.echo(f"Chunksize: {chunksize}")
    click.echo(f"Database: {db_name}, User: {db_user}")
    click.echo(f"Table: {db_table}")


def run():
    # program arguments
    year = 2021
    month = 1
    chunksize = 100000
    db_user = "postgres"
    db_password = "postgres"
    db_name = "ny_taxi"

    period = f"{year}-{month:02d}"
    db_table = f"yellow_taxi_data_{period}"

    # dataset source
    data_prefix = (
        "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow"
    )

    data_name = f"yellow_tripdata_{period}.csv.gz"
    data_source = f"{data_prefix}/{data_name}"

    print(f"[INFO] Starting data ingestion from\n{data_source}")

    # read dataset file in chunks
    df_iter = pd.read_csv(
        data_source,
        dtype=_DATA_SCHEMA,
        parse_dates=_DATE_COLUMNS,
        iterator=True,
        chunksize=chunksize,
    )

    # create db engine
    postgres_url = f"postgresql://{db_user}:{db_password}@{_DB_HOST}:5432/{db_name}"
    engine = create_engine(url=postgres_url)

    # insert dataset in database
    is_first = True
    total_inserted = 0

    for chunk in tqdm(df_iter, "Ingestion progress"):

        # create table, replace if exists
        if is_first:
            chunk.head(0).to_sql(
                name=db_table,
                con=engine,
                if_exists="replace",
            )
            is_first = False
            print(f"\n[INFO] Created new table {db_table}")

        # for each chunk, append rows to the table
        chunk.to_sql(
            name=db_table,
            con=engine,
            if_exists="append",
        )

        # progress info
        total_inserted += len(chunk)
        print(
            f"\n[INFO] Ingest data progress: inserted {len(chunk)} rows. Total {total_inserted} rows"
        )


if __name__ == "__main__":
    run()
