/* @bruin

# Docs:
# - SQL assets: https://getbruin.com/docs/bruin/assets/sql
# - Materialization: https://getbruin.com/docs/bruin/assets/materialization
# - Quality checks: https://getbruin.com/docs/bruin/quality/available_checks

# Report asset: daily aggregates by pickup zone
name: reports.trips_report

# Platform type
type: duckdb.sql

depends:
  - staging.trips

materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_datetime
  time_granularity: date

columns:
  - name: pickup_date
    type: date
    description: "Trip pickup date (derived from pickup_datetime)"
    primary_key: true

  - name: pickup_location_id
    type: integer
    description: "TLC taxi zone id where trip started"
    primary_key: true

  - name: trips_count
    type: bigint
    description: "Number of trips for the date + pickup zone"
    checks:
      - name: non_negative

  - name: total_amount
    type: float
    description: "The total amount for the group"

  - name: total_fare
    type: float
    description: "Sum of fare_amount for the group"

  - name: total_tip
    type: float
    description: "Sum of tip_amount for the group"
    checks:
      - name: non_negative

  - name: avg_trip_distance
    type: float
    description: "Average trip distance (miles)"
    checks:
      - name: non_negative

  - name: avg_passengers
    type: float
    description: "Average passenger count per trip"

@bruin */

-- Daily report aggregated by pickup zone
-- Uses {{ start_datetime }} / {{ end_datetime }} for incremental runs

SELECT
  CAST(pickup_datetime AS DATE) AS pickup_date,
  pickup_location_id,
  COUNT(*)::bigint AS trips_count,
  SUM(total_amount) AS total_amount,
  SUM(fare_amount) AS total_fare,
  SUM(COALESCE(tip_amount, 0.0)) AS total_tip,
  AVG(COALESCE(trip_distance, 0.0)) AS avg_trip_distance,
  AVG(COALESCE(passenger_count, 0.0)) AS avg_passengers
FROM staging.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
GROUP BY
  CAST(pickup_datetime AS DATE),
  pickup_location_id
ORDER BY
  pickup_date,
  pickup_location_id
