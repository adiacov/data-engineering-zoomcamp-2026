/* @bruin

# Docs:
# - Materialization: https://getbruin.com/docs/bruin/assets/materialization
# - Quality checks (built-ins): https://getbruin.com/docs/bruin/quality/available_checks
# - Custom checks: https://getbruin.com/docs/bruin/quality/custom

# TODO: Set the asset name (recommended: staging.trips).
name: staging.trips

# TODO: Set platform type.
# Docs: https://getbruin.com/docs/bruin/assets/sql
# suggested type: duckdb.sql
type: duckdb.sql

# TODO: Declare dependencies so `bruin run ... --downstream` and lineage work.
# Examples:
# depends:
#   - ingestion.trips
#   - ingestion.payment_lookup
depends:
  - ingestion.payment_lookup
  - ingestion.trips

# TODO: Choose time-based incremental processing if the dataset is naturally time-windowed.
# - This module expects you to use `time_interval` to reprocess only the requested window.
materialization:
  # What is materialization?
  # Materialization tells Bruin how to turn your SELECT query into a persisted dataset.
  # Docs: https://getbruin.com/docs/bruin/assets/materialization
  #
  # Materialization "type":
  # - table: persisted table
  # - view: persisted view (if the platform supports it)
  type: table

  # TODO: set a materialization strategy.
  # Docs: https://getbruin.com/docs/bruin/assets/materialization
  # suggested strategy: time_interval
  #
  # Incremental strategies (what does "incremental" mean?):
  # Incremental means you update only part of the destination instead of rebuilding everything every run.
  # In Bruin, this is controlled by `strategy` plus keys like `incremental_key` and `time_granularity`.
  #
  # Common strategies you can choose from (see docs for full list):
  # - create+replace (full rebuild)
  # - truncate+insert (full refresh without drop/create)
  # - append (insert new rows only)
  # - delete+insert (refresh partitions based on incremental_key values)
  # - merge (upsert based on primary key)
  # - time_interval (refresh rows within a time window)
  strategy: time_interval

  # TODO: set incremental_key to your event time column (DATE or TIMESTAMP).
  incremental_key: pickup_datetime

  # TODO: choose `date` vs `timestamp` based on the incremental_key type.
  time_granularity: date

parameters:
  enforce_schema: true

# TODO: Define output columns, mark primary keys, and add a few checks.
columns:
  # Identifiers
  - name: vendor_id
    type: integer
    description: "A code indicating the TPEP provider that provided the record."

  - name: ratecode_id
    type: integer
    description: "The final rate code in effect at the end of the trip."

  - name: pickup_location_id
    type: integer
    description: "TLC Taxi Zone in which the taximeter was engaged"

  - name: dropoff_location_id
    type: integer
    description: "TLC Taxi Zone in which the taximeter was disengaged"

  # Timestamps
  - name: pickup_datetime
    type: timestamp
    description: "The date and time when the meter was engaged."

  - name: dropoff_datetime
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

  # Derived
  - name: service_type
    type: string
    description: "Taxi service type"


# TODO: Add one custom check that validates a staging invariant (uniqueness, ranges, etc.)
# Docs: https://getbruin.com/docs/bruin/quality/custom
custom_checks:
  - name: custom_check_not_empty
    description: "Check whether the object is created and non empty"
    query: |
      -- TODO: return a single scalar (COUNT(*), etc.) that should match `value`
      SELECT COUNT(*) > 1 FROM staging.trips
    value: 1

@bruin */

-- TODO: Write the staging SELECT query.
--
-- Purpose of staging:
-- - Clean and normalize schema from ingestion
-- - Deduplicate records (important if ingestion uses append strategy)
-- - Enrich with lookup tables (JOINs)
-- - Filter invalid rows (null PKs, negative values, etc.)
--
-- Why filter by {{ start_datetime }} / {{ end_datetime }}?
-- When using `time_interval` strategy, Bruin:
--   1. DELETES rows where `incremental_key` falls within the run's time window
--   2. INSERTS the result of your query
-- Therefore, your query MUST filter to the same time window so only that subset is inserted.
-- If you don't filter, you'll insert ALL data but only delete the window's data = duplicates.

with ingestion_trips as (
  select * from ingestion.trips
),

payment_lookup as (
  select * from ingestion.payment_lookup
),

renamed as (
  select 
    -- Identifiers
    s.vendor_id,
    s.ratecode_id,
    s.pu_location_id as pickup_location_id,
    s.do_location_id as dropoff_location_id,
    -- Timestamps
    s.lpep_pickup_datetime as pickup_datetime,
    s.lpep_dropoff_datetime as dropoff_datetime,
    -- Trip details 
    s.passenger_count,
    s.trip_type,
    s.trip_distance,
    s.store_and_fwd_flag,
    -- Payment details 
    s.payment_type,
    p.payment_type_name,
    s.fare_amount,
    s.extra,
    s.mta_tax,
    s.tip_amount,
    s.tolls_amount,
    s.improvement_surcharge,
    s.total_amount,
    s.congestion_surcharge,
    s.airport_fee,
    s.cbd_congestion_fee,
    -- Derived 
    'Green' as service_type
  from ingestion_trips s
  join payment_lookup p
    on s.payment_type = p.payment_type_id
),

numbered as (
  select
    *,
    row_number()
    over (
      partition by 
        vendor_id, 
        pickup_datetime, 
        dropoff_datetime, 
        pickup_location_id, 
        dropoff_location_id
      ) as row_num
  from renamed
),

deduped as (
  select * 
  from numbered
  where row_num = 1
)

SELECT *
FROM deduped
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
