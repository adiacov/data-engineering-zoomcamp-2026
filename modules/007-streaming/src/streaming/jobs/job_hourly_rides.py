from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    BigInteger,
    Float,
    TIMESTAMP,
)

PROCESSED_EVENTS_TABLE = "processed_events_aggregated"


def source_events_kafka(t_env):
    table_name = "events"
    source_ddl = f"""
        CREATE TABLE {table_name} (
            pickup_location_id INTEGER,
            dropoff_location_id INTEGER,
            trip_distance DOUBLE,
            total_amount DOUBLE,
            pickup_datetime BIGINT,
            event_timestamp AS TO_TIMESTAMP_LTZ(pickup_datetime, 3),
            WATERMARK for event_timestamp as event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda:9092',
            'topic' = 'taxi-rides',
            'scan.startup.mode' = 'earliest-offset',
            'properties.auto.offset.reset' = 'earliest',
            'format' = 'json'
        );
    """

    t_env.execute_sql(source_ddl)
    return table_name


def sink_events_postgres(t_env):
    table_name = PROCESSED_EVENTS_TABLE
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            window_start TIMESTAMP(3),
            pickup_location_id INTEGER,
            num_trips BIGINT,
            total_revenue DOUBLE,
            PRIMARY KEY (window_start, pickup_location_id) NOT ENFORCED
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
    env.set_parallelism(3)

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
                    window_start,
                    pickup_location_id,
                    COUNT(*) AS num_trips,
                    SUM(total_amount) AS total_revenue
                FROM TABLE (
                    TUMBLE(TABLE {source}, DESCRIPTOR(event_timestamp), INTERVAL '1' HOUR)
                )
                GROUP BY window_start, pickup_location_id;
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
        Column("window_start", TIMESTAMP, primary_key=True),
        Column("pickup_location_id", Integer, primary_key=True),
        Column("num_trips", BigInteger),
        Column("total_revenue", Float),
    )

    metadata.create_all(engine)


if __name__ == "__main__":
    create_processed_events_table()
    log_processing()
