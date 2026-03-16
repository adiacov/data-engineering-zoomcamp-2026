import dataclasses
from datetime import datetime
import json
import pandas as pd


@dataclasses.dataclass
class Ride:
    pickup_datetime: int
    pickup_location_id: int
    dropoff_location_id: int
    trip_distance: float
    tip_amount: float
    total_amount: float
    
    def rides(limit: int = 100) -> pd.DataFrame:
        """Read dataset and return cleaned dataframe"""

        URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"

        columns = {
            "lpep_pickup_datetime": "datetime64[ns]",
            "PULocationID": "int32",
            "DOLocationID": "int32",
            "trip_distance": "float32",
            "tip_amount": "float32",
            "total_amount": "float32",
        }

        cols_renamed = {
            "lpep_pickup_datetime": "pickup_datetime",
            "PULocationID": "pickup_location_id",
            "DOLocationID": "dropoff_location_id",
        }

        try:
            df = (
                pd.read_parquet(
                    URL,
                    columns=list(columns),
                )
                .head(limit)
                .astype(columns)
                .rename(columns=cols_renamed)
            )

            # Convert datetime -> epoch milliseconds
            df["pickup_datetime"] = df["pickup_datetime"].astype("int64") // 10**6

        except ImportError as e:
            print(f"[ERROR]: {e}")
            print("Please install pyarrow or fastparquet to enable Parquet support.")
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")

        return df

    def rides_no_limit() -> pd.DataFrame:
        """Read dataset and return cleaned dataframe"""

        URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"

        columns = {
            "lpep_pickup_datetime": "datetime64[ns]",
            "PULocationID": "int32",
            "DOLocationID": "int32",
            "trip_distance": "float32",
            "tip_amount": "float32",
            "total_amount": "float32",
        }

        cols_renamed = {
            "lpep_pickup_datetime": "pickup_datetime",
            "PULocationID": "pickup_location_id",
            "DOLocationID": "dropoff_location_id",
        }

        try:
            df = (
                pd.read_parquet(
                    URL,
                    columns=list(columns),
                )
                .astype(columns)
                .rename(columns=cols_renamed)
            )

            # Convert datetime -> epoch milliseconds
            df["pickup_datetime"] = df["pickup_datetime"].astype("int64") // 10**6

        except ImportError as e:
            print(f"[ERROR]: {e}")
            print("Please install pyarrow or fastparquet to enable Parquet support.")
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")

        return df

    def from_record(row):
        """Returns a Ride object from a record"""
        return Ride(**row)

    def value_serializer(ride):
        """Serializes Ride object to bytes"""
        ride_dict = dataclasses.asdict(ride)
        json_str = json.dumps(ride_dict)
        return json_str.encode("utf-8")

    def value_deserializer(msg):
        """Deserializes bytes to a Ride object"""
        msg_str = msg.decode("utf-8")
        ride_dict = json.loads(msg_str)
        return Ride(**ride_dict)

    def value_json_deserializer(json_data):
        """Deserializes json to a Ride object"""
        return Ride(**json_data)
