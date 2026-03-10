from kafka import KafkaConsumer
from streaming.model import Ride
import dataclasses
import time

from sqlalchemy import Table, MetaData, Column, Integer, Float, DateTime, create_engine

# Config
BATCH_SIZE = 1000
BATCH_TIMEOUT_SEC = 5


def create_consumer(topic):
    """Returns a configured KafkaConsumer"""
    return KafkaConsumer(
        topic,
        bootstrap_servers=["localhost:19092"],
        client_id="consumer_db_1",
        group_id="consumer_db_group",
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        max_poll_records=BATCH_SIZE,
        fetch_max_wait_ms=500,
        value_deserializer=Ride.value_deserializer,
    )


def create_table(table_name, engine):
    """Creates the taxi_rides table if it doesn't exist"""
    metadata = MetaData()
    rides_table = Table(
        table_name,
        metadata,
        Column("pickup_datetime", DateTime),
        Column("dropoff_datetime", DateTime),
        Column("pickup_location_id", Integer),
        Column("dropoff_location_id", Integer),
        Column("passenger_count", Integer),
        Column("trip_distance", Float),
        Column("tip_amount", Float),
        Column("total_amount", Float),
    )
    metadata.create_all(engine)
    return rides_table


def get_engine():
    """Creates SQLAlchemy Engine"""
    return create_engine("postgresql+psycopg2://postgres:postgres@localhost/ny_taxi")


def insert_rides(rides, engine, table):
    """Stores taxi ride objects into the database"""
    rides_batch = [dataclasses.asdict(ride) for ride in rides]
    with engine.begin() as con:
        con.execute(table.insert(), rides_batch)
    print(f"[INFO] Inserted {len(rides_batch)} rides into DB")


def consume(topic, engine, table):
    """Consumes messages from Kafka and writes to the database in batches"""
    consumer = create_consumer(topic)
    buffer = []
    last_flush_time = time.time()
    last_offsets = {}  # track last offset per partition

    try:
        for message in consumer:
            buffer.append(message.value)
            last_offsets[(message.topic, message.partition)] = message.offset

            now = time.time()
            # Flush based on batch size or timeout
            if len(buffer) >= BATCH_SIZE or (
                buffer and now - last_flush_time >= BATCH_TIMEOUT_SEC
            ):
                insert_rides(buffer, engine, table)
                consumer.commit()

                # Log last offsets per partition
                for (topic_name, partition), offset in last_offsets.items():
                    print(
                        f"[INFO] topic={topic_name} partition={partition} last_offset={offset}"
                    )

                buffer.clear()
                last_flush_time = now
                last_offsets.clear()

    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt received, stopping consumer...")

    finally:
        # Flush remaining messages on shutdown
        if buffer:
            insert_rides(buffer, engine, table)
            consumer.commit()
            for (topic_name, partition), offset in last_offsets.items():
                print(
                    f"[INFO] topic={topic_name} partition={partition} last_offset={offset}"
                )

        consumer.close()
        print("[INFO] Consumer APP stopped")


def main():
    print("[INFO] Starting consumer APP")
    print("[INFO] Type CTRL + C to stop the consumer APP")

    engine = get_engine()
    table = create_table("taxi_rides", engine)
    consume("test-topic", engine, table)


if __name__ == "__main__":
    main()
