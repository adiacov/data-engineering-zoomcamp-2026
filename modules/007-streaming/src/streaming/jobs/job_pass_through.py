from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, TIMESTAMP

PROCESSED_EVENTS_TABLE = "processed_events"


def source_events_kafka(t_env):
    table_name = "events"
    source_ddl = f"""
        CREATE TABLE {table_name} (
            pickup_location_id INTEGER,
            dropoff_location_id INTEGER,
            trip_distance DOUBLE,
            total_amount DOUBLE,
            pickup_datetime BIGINT
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda:9092',
            'topic' = 'taxi-rides',
            'scan.startup.mode' = 'latest-offset',
            'properties.auto.offset.reset' = 'latest',
            'format' = 'json'
        );
    """

    t_env.execute_sql(source_ddl)
    return table_name


def sink_events_postgres(t_env):
    table_name = PROCESSED_EVENTS_TABLE
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            pickup_location_id INTEGER,
            dropoff_location_id INTEGER,
            trip_distance DOUBLE,
            total_amount DOUBLE,
            pickup_datetime TIMESTAMP
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/ny_taxi',
            'table-name' = '{PROCESSED_EVENTS_TABLE}',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'  
        );
    """

    t_env.execute_sql(sink_ddl)
    return table_name


def log_processing():
    # set execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)  # checkpoint every 10 seconds

    # set table environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, settings)

    try:
        # create kafka table
        source = source_events_kafka(t_env)
        sink = sink_events_postgres(t_env)

        # write records to postgres
        t_env.execute_sql(
            f"""
                INSERT INTO {sink}
                SELECT
                    pickup_location_id,
                    dropoff_location_id,
                    trip_distance,
                    total_amount,
                    TO_TIMESTAMP_LTZ(pickup_datetime, 3) as pickup_datetime
                FROM {source}
            """
        ).wait()

    except Exception as e:
        print("[ERROR] Stream Table failed: ", str(e))


def create_processed_events_table():
    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@postgres:5432/ny_taxi"
    )

    metadata = MetaData()

    Table(
        PROCESSED_EVENTS_TABLE,
        metadata,
        Column("pickup_location_id", Integer),
        Column("dropoff_location_id", Integer),
        Column("trip_distance", Float),
        Column("total_amount", Float),
        Column("pickup_datetime", TIMESTAMP),
    )

    metadata.create_all(engine)


if __name__ == "__main__":
    create_processed_events_table()
    log_processing()
