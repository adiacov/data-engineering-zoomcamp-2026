from pyspark.sql import SparkSession
from pyspark.sql import types
import pyspark.sql.functions as F

import argparse

from common.config import get_root_path

# Handle program arguments
parser = argparse.ArgumentParser("Clean Taxi Dataset")


parser.add_argument(
    "--taxi-type",
    required=True,
    choices=["green", "yellow"],
    help="Taxi dataset type. One of [green, yellow]",
)
parser.add_argument("--year", required=True, help="Taxi dataset year.")
parser.add_argument("--month", required=True, help="Taxi dataset month number.")

args = parser.parse_args()

taxi_type = args.taxi_type
year = args.year
month = f"{int(args.month):02d}"


# Declare dataset paths
TAXI_PATH = get_root_path() / "data" / "taxi"
DATASET_RAW_PATH = TAXI_PATH / "ingestion" / taxi_type / year / month
DATASET_CLEAN_PATH = TAXI_PATH / "clean" / taxi_type / year / month


# Create a spark session
spark = SparkSession.builder.master("local[*]").appName("taxi-rides-app").getOrCreate()

print("[INFO] Starting spark session")

if not spark.version:
    print("[ERROR] Could not start SPARK session. Exiting program.")
    import os

    exit(1)

# Program
print(f"[INFO] Reading raw dataset {taxi_type}/{year}/{month}")
dataset_file_path = str(DATASET_RAW_PATH)
df = spark.read.parquet(dataset_file_path)

# Normalize - rename columns, group columns
print("[INFO] Normalizing dataset")
if taxi_type == "green":
    cols_renamed = {
        "VendorID": "vendor_id",
        "RatecodeID": "rate_code_id",
        "PULocationID": "pickup_location_id",
        "DOLocationID": "dropoff_location_id",
        "lpep_pickup_datetime": "pickup_datetime",
        "lpep_dropoff_datetime": "dropoff_datetime",
    }
elif taxi_type == "yellow":
    cols_renamed = {
        "VendorID": "vendor_id",
        "RatecodeID": "rate_code_id",
        "PULocationID": "pickup_location_id",
        "DOLocationID": "dropoff_location_id",
        "tpep_pickup_datetime": "pickup_datetime",
        "tpep_dropoff_datetime": "dropoff_datetime",
        "Airport_fee": "airport_fee",
    }
else:
    print(
        f"[ERROR] Unsupported taxi_type: {taxi_type}, Expected one of [green, yellow]."
    )
    exit(1)

df = df.withColumnsRenamed(cols_renamed)

# Normalize - add column to identify dataset source
df = df.withColumn("service_type", F.lit(taxi_type))

zero_fee_col = F.lit(0.0).cast(types.FloatType())

if taxi_type == "green":
    # Green taxi not allowed to pickup at airports. Always zero.
    df = df.withColumn("airport_fee", zero_fee_col)
elif taxi_type == "yellow":
    # ehail_fee not applicable to yellow. Always zero.
    # trip_type always 1 (Street Hail) for yellow taxi
    df = df.withColumn("ehail_fee", zero_fee_col).withColumn(
        "trip_type", F.lit(1).cast(types.IntegerType())
    )


else:
    print(
        f"[ERROR] Unsupported taxi_type: {taxi_type}, Expected one of [green, yellow]."
    )
    exit(1)

# Define final dataset schema
# Original schema contains Double and Long types. Cast to Float, Integer.
target_schema = types.StructType(
    [
        types.StructField("vendor_id", types.IntegerType(), True),
        types.StructField("pickup_datetime", types.TimestampNTZType(), True),
        types.StructField("dropoff_datetime", types.TimestampNTZType(), True),
        types.StructField("store_and_fwd_flag", types.StringType(), True),
        types.StructField("rate_code_id", types.IntegerType(), True),
        types.StructField("pickup_location_id", types.IntegerType(), True),
        types.StructField("dropoff_location_id", types.IntegerType(), True),
        types.StructField("passenger_count", types.IntegerType(), True),
        types.StructField("trip_distance", types.FloatType(), True),
        types.StructField("fare_amount", types.FloatType(), True),
        types.StructField("extra", types.FloatType(), True),
        types.StructField("mta_tax", types.FloatType(), True),
        types.StructField("tip_amount", types.FloatType(), True),
        types.StructField("tolls_amount", types.FloatType(), True),
        types.StructField("ehail_fee", types.FloatType(), True),
        types.StructField("improvement_surcharge", types.FloatType(), True),
        types.StructField("total_amount", types.FloatType(), True),
        types.StructField("payment_type", types.IntegerType(), True),
        types.StructField("trip_type", types.IntegerType(), True),
        types.StructField("congestion_surcharge", types.FloatType(), True),
        types.StructField("cbd_congestion_fee", types.FloatType(), True),
        types.StructField("service_type", types.StringType(), True),
        types.StructField("airport_fee", types.FloatType(), True),
    ]
)

# Cast dataframe fields to final schema
cast_columns = [
    F.col(field.name).cast(field.dataType) for field in target_schema.fields
]

df = df.select(*cast_columns)

print(f"[INFO] Loading cleaned dataset {taxi_type}/{year}/{month}")
df.repartition(4).write.parquet(
    path=str(DATASET_CLEAN_PATH),
    mode="overwrite",
)

spark.stop()
