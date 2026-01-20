-- Active: 1768805813169@@localhost@5432@ny_taxi@public

-- metadata
select *
from information_schema.tables
where
    table_name like 'yellow_taxi_data%';

select *
from information_schema.tables
where
    table_name like 'taxi_zones%';

select count(1) from public.yellow_taxi_data_2021_01;

select * from public.yellow_taxi_data_2021_01 limit 1;

select count(1) from public.taxi_zones_lookup;

select * from public.taxi_zones_lookup limit 1;

-- yellow_taxi_data_2021_01 columns
-- index                   :   int <- this is from pandas
-- VendorID                :   int
-- tpep_pickup_datetime    :   timestamp without time zone
-- tpep_dropoff_datetime   :   timestamp without time zone
-- passenger_count         :   int
-- trip_distance           :   float
-- RatecodeID              :   int
-- store_and_fwd_flag      :   text
-- PULocationID            :   int
-- DOLocationID            :   int
-- payment_type            :   int
-- fare_amount             :   float
-- extra                   :   float
-- mta_tax                 :   float
-- tip_amount              :   float
-- tolls_amount            :   float
-- improvement_surcharge   :   float
-- total_amount            :   float
-- congestion_surcharge    :   float

-- taxi_zones_lookup columns
-- index        :    int <-- this is from pandas
-- LocationID   :    int
-- Borough      :    text
-- Zone         :    text
-- service_zone :    text

-- SQL refresher

-- Select certain columns without using table JOIN, and only using WHERE
-- !!! TOO SLOW IN VSCODE. Use pgAdmin directly
-- EXPLAIN
SELECT
    t.tpep_pickup_datetime,
    t.tpep_dropoff_datetime,
    t.total_amount,
    concat(
        zpu."Borough",
        ' / ',
        zpu."Zone"
    ) AS pickup_loc,
    concat(
        zdo."Borough",
        ' / ',
        zdo."Zone"
    ) AS dropoff_loc
FROM
    yellow_taxi_data_2021_01 t,
    taxi_zones_lookup zpu,
    taxi_zones_lookup zdo
WHERE
    t."PULocationID" = zpu."LocationID"
    AND t."DOLocationID" = zdo."LocationID"
LIMIT 100;

-- Same query as above, only this time using JOIN
-- !!! TOO SLOW IN VSCODE. Use pgAdmin directly
SELECT
    t.tpep_pickup_datetime,
    t.tpep_dropoff_datetime,
    t.total_amount,
    concat(
        zpu."Borough",
        ' / ',
        zpu."Zone"
    ) AS pickup_loc,
    concat(
        zdo."Borough",
        ' / ',
        zdo."Zone"
    ) AS dropoff_loc
FROM
    yellow_taxi_data_2021_01 t
    JOIN taxi_zones_lookup zpu ON t."PULocationID" = zpu."LocationID"
    JOIN taxi_zones_lookup zdo ON t."DOLocationID" = zdo."LocationID"
LIMIT 100;

-- Check for any missing values in Location columns
SELECT COUNT(*)
FROM yellow_taxi_data_2021_01
WHERE
    "PULocationID" IS NULL;

SELECT COUNT(*)
FROM yellow_taxi_data_2021_01
WHERE
    "DOLocationID" IS NULL;

-- Check for Location columns which aren't present in the taxi_zones_lookup table
SELECT COUNT(*)
FROM yellow_taxi_data_2021_01
WHERE
    "PULocationID" NOT IN (
        SELECT "LocationID"
        FROM taxi_zones_lookup
    );

SELECT COUNT(*)
FROM yellow_taxi_data_2021_01
WHERE
    "DOLocationID" NOT IN (
        SELECT "LocationID"
        FROM taxi_zones_lookup
    );

-- At this point we have a good dataset regarding the location columns.
-- There are no missing location values in the yellow_taxi_data table.
-- There are no unknown (additional, mistake) locations present in yellow_taxi_data, but missing in the taxi_zones_lookup table;

-- Show how many record there are per day
SELECT
    CAST(tpep_dropoff_datetime AS DATE) as day,
    count(1) AS records,
    MAX(total_amount) AS max_total_amount,
    MAX(passenger_count) AS max_passenger_count
FROM yellow_taxi_data_2021_01
GROUP BY
    day
ORDER BY records DESC;

--- Module 1 Homework: Docker & SQL
-- datasets: green_taxi_data_2025_11, taxi_zone_lookup

select count(1) from green_taxi_data_2025_11;

select * from green_taxi_data_2025_11 limit 10;

-- Question 3. Counting short trips
-- For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a trip_distance of less than or equal to 1 mile?

SELECT COUNT(1)
FROM green_taxi_data_2025_11
WHERE (
        lpep_pickup_datetime >= '2025-11-01'
        AND lpep_dropoff_datetime < '2025-12-01'
    )
    AND trip_distance <= 1;

-- **Answer:** 8007

-- Question 4. Longest trip for each day
-- Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles (to exclude data errors).

SELECT CAST(lpep_pickup_datetime AS DATE) AS day, MAX(trip_distance) AS max_trip_distance
FROM green_taxi_data_2025_11
WHERE
    trip_distance < 100
GROUP BY
    day
ORDER BY max_trip_distance DESC;

-- **Answer:** 2025-11-14

-- Question 5. Biggest pickup zone
-- Which was the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025?

SELECT zpu."Zone", SUM(g.total_amount) AS total_amount
FROM
    green_taxi_data_2025_11 g
    JOIN taxi_zones_lookup zpu ON g."PULocationID" = zpu."LocationID"
WHERE
    CAST(lpep_pickup_datetime AS DATE) = '2025-11-18'
GROUP BY
    zpu."Zone"
ORDER BY total_amount DESC;

-- **Answer:** East Harlem North

-- Question 6. Largest tip
-- For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip

SELECT zdo."Zone", MAX(t.tip_amount) AS max_tip_amount
FROM
    green_taxi_data_2025_11 t
    JOIN taxi_zones_lookup zpu ON t."PULocationID" = zpu."LocationID"
    JOIN taxi_zones_lookup zdo ON t."DOLocationID" = zdo."LocationID"
WHERE
    zpu."Zone" = 'East Harlem North'
GROUP BY
    zdo."Zone"
ORDER BY max_tip_amount DESC;

-- **Answer:** Yorkville West