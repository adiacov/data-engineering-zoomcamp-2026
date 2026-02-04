
-- BigQuery Setup

-- Create an external table using the Yellow Taxi Trip Records.
CREATE OR REPLACE EXTERNAL TABLE `taxi_rides_ny.external_yellow_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris=['gs://de_course_bucket/taxi/parquet/yellow_tripdata_2024-*.parquet']

);

SELECT COUNT(1) FROM `taxi_rides_ny.external_yellow_tripdata`;

-- Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table).
CREATE OR REPLACE TABLE `taxi_rides_ny.yellow_tripdata` AS
SELECT * FROM `taxi_rides_ny.external_yellow_tripdata`;

-- Question 1. Counting records

-- What is count of records for the 2024 Yellow Taxi Data?
-- Options:
--  65,623
--  840,402
--  20,332,093
--  85,431,289

SELECT COUNT(1) FROM `taxi_rides_ny.yellow_tripdata`;

-- **Answer** 20,332,093


-- Question 2. Data read estimation
-- Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
-- What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?
-- Options:
-- 18.82 MB for the External Table and 47.60 MB for the Materialized Table
-- 0 MB for the External Table and 155.12 MB for the Materialized Table
-- 2.14 GB for the External Table and 0MB for the Materialized Table
-- 0 MB for the External Table and 0MB for the Materialized Table

SELECT COUNT(DISTINCT(PULocationID)) FROM `taxi_rides_ny.external_yellow_tripdata`

SELECT COUNT(DISTINCT(PULocationID)) FROM `taxi_rides_ny.yellow_tripdata`;

-- **Answer** 0 MB for the External Table and 155.12 MB for the Materialized Table


-- Question 3. Understanding columnar storage

-- Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table.
-- Why are the estimated number of Bytes different?
-- Options:
-- BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.
-- BigQuery duplicates data across multiple storage partitions, so selecting two columns instead of one requires scanning the table twice, doubling the estimated bytes processed.
-- BigQuery automatically caches the first queried column, so adding a second column increases processing time but does not affect the estimated bytes scanned.
-- When selecting multiple columns, BigQuery performs an implicit join operation between them, increasing the estimated bytes processed

SELECT PULocationID FROM `taxi_rides_ny.yellow_tripdata`;

SELECT PULocationID, DOLocationID FROM `taxi_rides_ny.yellow_tripdata`;

-- **Answer**

