import dataclasses
from datetime import datetime
import json


@dataclasses.dataclass
class Ride:
    pickup_datetime: datetime
    dropoff_datetime: datetime
    pickup_location_id: int
    dropoff_location_id: int
    passenger_count: int
    trip_distance: float
    tip_amount: float
    total_amount: float

    def rides():
        """Read a csv dataset file and returns a pandas DataFrame.

        The final dataframe has a subset of columns, renamed, casted
        and removed rows containing null values.
        """
        import pandas as pd
        from common.config import get_root_path

        FILE = get_root_path() / "data" / "green_tripdata_2019-10.csv.gz"
        columns = {
            "lpep_pickup_datetime": "datetime64[ns]",
            "lpep_dropoff_datetime": "datetime64[ns]",
            "PULocationID": "int32",
            "DOLocationID": "int32",
            "passenger_count": "int32",
            "trip_distance": "float32",
            "tip_amount": "float32",
            "total_amount": "float32",
        }

        cols_renamed = {
            "lpep_pickup_datetime": "pickup_datetime",
            "lpep_dropoff_datetime": "dropoff_datetime",
            "PULocationID": "pickup_location_id",
            "DOLocationID": "dropoff_location_id",
        }

        df = (
            pd.read_csv(str(FILE), usecols=list(columns))
            .dropna()
            .astype(columns)
            .rename(columns=cols_renamed)
        )

        return df

    def from_record(row):
        """Returns a Ride object from a record (e.g. pandas)"""
        return Ride(**row)

    def value_serializer(ride):
        """Serializes Ride object to bytes"""

        def default(obj):
            if isinstance(obj, datetime):
                return datetime.isoformat(obj)
            raise TypeError(f"Cannot serialize {type(obj)}")

        ride_dict = dataclasses.asdict(ride)
        json_str = json.dumps(ride_dict, default=default)
        return json_str.encode("utf-8")

    def value_deserializer(msg):
        """Deserializes bytes to a Ride object"""

        def hook(data):
            if "pickup_datetime" in data:
                data["pickup_datetime"] = datetime.fromisoformat(
                    data["pickup_datetime"]
                )
            elif "dropoff_datetime" in data:
                data["dropoff_datetime"] = datetime.fromisoformat(
                    data["dropoff_datetime"]
                )
            return data

        msg_str = msg.decode("utf-8")
        ride_dict = json.loads(msg_str, object_hook=hook)
        return Ride(**ride_dict)
