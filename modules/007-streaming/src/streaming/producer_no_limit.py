from kafka import KafkaProducer
from streaming.model import Ride
import pandas as pd
from common.benchmark import benchmark


def on_success(metadata):
    print(f"[INFO] Message produced: {metadata}")


def on_error(e):
    print(f"[ERROR] Error sending message: {e}")


@benchmark
def main():
    print("[INFO] Starting Producer APP.")

    producer = KafkaProducer(
        bootstrap_servers=["localhost:19092"],
        request_timeout_ms=2000,
        api_version_auto_timeout_ms=2000,
        value_serializer=Ride.value_serializer,
    )

    topic = "taxi-rides"

    rides: pd.DataFrame = Ride.rides_no_limit()
    for record in rides.to_dict(orient="records"):
        ride = Ride.from_record(record)
        future = producer.send(
            topic=topic,
            value=ride,
        )

        future.add_callback(on_success)
        future.add_errback(on_error)

    producer.flush()
    producer.close()
    print("[INFO] Stop producer APP")


if __name__ == "__main__":
    main()
