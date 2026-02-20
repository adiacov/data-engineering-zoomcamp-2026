"""@bruin

# TODO: Set the asset name (recommended pattern: schema.asset_name).
# - Convention in this module: use an `ingestion.` schema for raw ingestion tables.
name: ingestion.trips

# TODO: Set the asset type.
# Docs: https://getbruin.com/docs/bruin/assets/python
type: python

# TODO: Pick a Python image version (Bruin runs Python in isolated environments).
# Example: python:3.11
image: python:3.11-alipine

# TODO: Set the connection.
connection: duckdb-zoomcamp

depends:
  -  ingestion.payment_lookup

# TODO: Choose materialization (optional, but recommended).
# Bruin feature: Python materialization lets you return a DataFrame (or list[dict]) and Bruin loads it into your destination.
# This is usually the easiest way to build ingestion assets in Bruin.
# Alternative (advanced): you can skip Bruin Python materialization and write a "plain" Python asset that manually writes
# into DuckDB (or another destination) using your own client library and SQL. In that case:
# - you typically omit the `materialization:` block
# - you do NOT need a `materialize()` function; you just run Python code
# Docs: https://getbruin.com/docs/bruin/assets/python#materialization
materialization:
  # TODO: choose `table` or `view` (ingestion generally should be a table)
  type: table
  # TODO: pick a strategy.
  # suggested strategy: append
  strategy: append

parameters:
  enforce_schema: true

columns:
  # Identifiers
  - name: VendorID
    type: integer
    description: "A code indicating the TPEP provider that provided the record."

  - name: RatecodeID
    type: integer
    description: "The final rate code in effect at the end of the trip."

  - name: PULocationID
    type: integer
    description: "TLC Taxi Zone in which the taximeter was engaged"

  - name: DOLocationID
    type: integer
    description: "TLC Taxi Zone in which the taximeter was disengaged"

  # Timestamps
  - name: lpep_pickup_datetime
    type: timestamp
    description: "The date and time when the meter was engaged."

  - name: lpep_dropoff_datetime
    type: timestamp
    description: "The date and time when the meter was disengaged."

  # Trip details
  - name: passenger_count
    type: integer
    description: "The number of passengers in the vehicle."

  # GREEN only (missing in YELLOW dataset; Uses default value; code 1 - street-hail always for yellow taxi)
  - name: trip_type
    type: integer
    description: |
      A code indicating whether the trip was a street-hail or a dispatch that is
      automatically assigned based on the metered rate in use but can be altered
      by the driver.
    default: 1

  - name: trip_distance
    type: float
    description: "The elapsed trip distance in miles reported by the taximeter."

  - name: store_and_fwd_flag
    type: string
    description: |
      This flag indicates whether the trip record was held in vehicle memory before
      sending to the vendor, aka “store and forward,” because the vehicle did not
      have a connection to the server.

  # Payment
  - name: payment_type
    type: integer
    description: "A numeric code signifying how the passenger paid for the trip."

  - name: fare_amount
    type: float
    description: "The time-and-distance fare calculated by the meter."

  - name: extra
    type: float
    description: "Miscellaneous extras and surcharges."

  - name: mta_tax
    type: float
    description: "Tax that is automatically triggered based on the metered rate in use."

  - name: tip_amount
    type: float
    description: "Tip amount – This field is automatically populated for credit card tips. Cash
tips are not included."

  - name: tolls_amount
    type: float
    description: "Total amount of all tolls paid in trip."

  - name: improvement_surcharge
    type: float
    description: "Improvement surcharge assessed trips at the flag drop. The improvement
surcharge began being levied in 2015."

  - name: total_amount
    type: float
    description: "The total amount charged to passengers. Does not include cash tips."

  - name: congestion_surcharge
    type: float
    description: "Total amount collected in trip for NYS congestion surcharge."

  # YELLOW only (missing in GREEN dataset; Uses default value; Green taxi aren't allowed to pickup at specified airports)
  - name: airport_fee
    type: float
    description: "For pick up only at LaGuardia and John F. Kennedy Airports."
    default: 0

  - name: cbd_congestion_fee
    type: float
    description: "Per-trip charge for MTA's Congestion Relief Zone starting Jan. 5, 2025."

@bruin"""

# TODO: Add imports needed for your ingestion (e.g., pandas, requests).
# - Put dependencies in the nearest `requirements.txt` (this template has one at the pipeline root).
# Docs: https://getbruin.com/docs/bruin/assets/python
import pandas as pd

import os
import json


# TODO: Only implement `materialize()` if you are using Bruin Python materialization.
# If you choose the manual-write approach (no `materialization:` block), remove this function and implement ingestion
# as a standard Python script instead.

# GREEN   https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-01.parquet
# YELLOW  https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def generate_months_to_ingest(start_date: str, end_date: str) -> list[tuple[int, int]]:
    try:
        start_year = int(start_date.split("-")[0])
        end_year = int(end_date.split("-")[0])
        start_month = int(start_date.split("-")[1])
        end_month = int(end_date.split("-")[1])

        result = []
        for year in range(start_year, end_year + 1):
            for month in range(start_month, end_month + 1):
                result.append((year, month))

        return result

    except Exception as e:
        print("<<< Could not generate ingestion dates")
        raise e


def build_parquet_url(taxi_type: str, year: int, month: int) -> str:
    # create an URL for a specific file on WEB
    taxi_file = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
    return f"{BASE_URL}/{taxi_file}"


def fetch_trip_data(taxi_type: str, year: int, month: int) -> pd.DataFrame:
    url = build_parquet_url(taxi_type, year, month)
    print(f"<<< Ingesting: {url}")
    return pd.read_parquet(url)


def materialize():
    """
    TODO: Implement ingestion using Bruin runtime context.

    Required Bruin concepts to use here:
    - Built-in date window variables:
      - BRUIN_START_DATE / BRUIN_END_DATE (YYYY-MM-DD)
      - BRUIN_START_DATETIME / BRUIN_END_DATETIME (ISO datetime)
      Docs: https://getbruin.com/docs/bruin/assets/python#environment-variables
    - Pipeline variables:
      - Read JSON from BRUIN_VARS, e.g. `taxi_types`
      Docs: https://getbruin.com/docs/bruin/getting-started/pipeline-variables

    Design TODOs (keep logic minimal, focus on architecture):
    - Use start/end dates + `taxi_types` to generate a list of source endpoints for the run window.
    - Fetch data for each endpoint, parse into DataFrames, and concatenate.
    - Add a column like `extracted_at` for lineage/debugging (timestamp of extraction).
    - Prefer append-only in ingestion; handle duplicates in staging.
    """

    start_date = os.environ.get("BRUIN_START_DATE")
    end_date = os.environ.get("BRUIN_END_DATE")

    dates = generate_months_to_ingest(start_date, end_date)

    vars = json.loads(os.environ.get("BRUIN_VARS"))
    taxi_types = vars["taxi_types"]

    result = pd.DataFrame()
    for taxi_type in taxi_types:
        for year, month in dates:
            df = fetch_trip_data(taxi_type, year, month)
            df["extracted_at"] = pd.Timestamp.now(tz="UTC")
            result = pd.concat([result, df], ignore_index=True)

    return result
