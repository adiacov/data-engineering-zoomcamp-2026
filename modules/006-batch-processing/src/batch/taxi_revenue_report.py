from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = (
    SparkSession.builder.master("local[*]").appName("taxi-revenue-report").getOrCreate()
)
spark.version

from common.config import get_root_path

# Declare dataset paths
DATA_PATH = get_root_path() / "data"
TAXI_PATH = DATA_PATH / "taxi"
DATASET_GREEN_PATH = TAXI_PATH / "clean" / "green" / "2025" / "11"
DATASET_YELLOW_PATH = TAXI_PATH / "clean" / "yellow" / "2025" / "11"
DATASET_ZONES = DATA_PATH / "taxi_zone_lookup.csv"
DATASET_REPORT_PATH = TAXI_PATH / "report" / "revenue"
REPORT_REVENUE_ZONE = DATASET_REPORT_PATH / "revenue_by_zone"  # total revenue per zone
REPORT_REVENUE_VENDOR_ZONE = (
    DATASET_REPORT_PATH / "revenue_by_vendor_zone"
)  # total revenue per vendor and zone

print("[INFO] Loading dataset clean/green/2025/11")
green_df = spark.read.parquet(str(DATASET_GREEN_PATH))

green_df = green_df.select(
    "vendor_id", "pickup_location_id", "total_amount"
).withColumnRenamed("pickup_location_id", "location_id")
green_df.columns

print("[INFO] Loading dataset clean/yellow/2025/11")
yellow_df = spark.read.parquet(str(DATASET_YELLOW_PATH))

yellow_df = yellow_df.select(
    "vendor_id", "pickup_location_id", "total_amount"
).withColumnRenamed("pickup_location_id", "location_id")
yellow_df.columns

print("[INFO] Combining green with yellow datasets")
df_combined = green_df.union(yellow_df)
df_combined.columns

print("[INFO] Loading dataset taxi_zone_lookup")
df_zones = (
    spark.read.csv(str(DATASET_ZONES), header=True)
    .withColumnsRenamed({"LocationId": "location_id", "Zone": "zone"})
    .select("location_id", "zone")
)

print("[INFO] Joining taxi with zones")
# broadcast: df_zones is small enough to copy it to all executors, for the later join with taxi dataset
df_zones = F.broadcast(df_zones)
df_joined = df_combined.join(df_zones, on="location_id")

print("[INFO] Generating report: total revenue by zone")
df_revenue_zone = (
    df_joined.groupBy("zone")
    .agg(F.sum("total_amount").cast("decimal(20, 2)").alias("revenue"))
    .sort(F.desc("revenue"))
)

print("[INFO] Generating report: total revenue by vendor_id and zone")
df_revenue_vendor_zone = (
    df_joined.groupBy("vendor_id", "zone")
    .agg(F.sum("total_amount").cast("decimal(20, 2)").alias("revenue"))
    .sort([F.col("vendor_id"), F.desc("revenue")])
)

print("[INFO] Writing report to file: revenue by zon")
df_revenue_zone.write.parquet(str(REPORT_REVENUE_ZONE), mode="overwrite")
print("[INFO] Writing report to file: revenue by vendor_id and zone")
df_revenue_vendor_zone.write.parquet(str(REPORT_REVENUE_VENDOR_ZONE), mode="overwrite")
