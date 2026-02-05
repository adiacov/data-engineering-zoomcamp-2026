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
-- 155.12 MB to process

SELECT PULocationID, DOLocationID FROM `taxi_rides_ny.yellow_tripdata`;
-- 310.24 MB to process

SELECT PULocationID, DOLocationID, tip_amount FROM `taxi_rides_ny.yellow_tripdata`;
-- 465.36 MB to process

SELECT * FROM `taxi_rides_ny.yellow_tripdata`;
-- 2.72 GB to process

-- **Answer** BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.

-- Question 4. Counting zero fare trips

-- How many records have a fare_amount of 0?
-- Options:
-- 128,210
-- 546,578
-- 20,188,016
-- 8,333
SELECT COUNT(1) FROM `taxi_rides_ny.yellow_tripdata` WHERE fare_amount = 0;
-- 155.12 MB to process

-- **Answer** 8,333

-- Question 5. Partitioning and clustering

-- What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)
-- Options:
-- Partition by tpep_dropoff_datetime and Cluster on VendorID
-- Cluster on by tpep_dropoff_datetime and Cluster on VendorID
-- Cluster on tpep_dropoff_datetime Partition by VendorID
-- Partition by tpep_dropoff_datetime and Partition by VendorID

CREATE OR REPLACE TABLE `taxi_rides_ny.partitioned_yellow_tripdata`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS SELECT * FROM `taxi_rides_ny.external_yellow_tripdata`;

-- **Answer** Partition by tpep_dropoff_datetime and Cluster on VendorID

-- Question 6. Partition benefits
-- Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive)

-- Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values?

-- Choose the answer which most closely matches.

-- 12.47 MB for non-partitioned table and 326.42 MB for the partitioned table
-- 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table
-- 5.87 MB for non-partitioned table and 0 MB for the partitioned table
-- 310.31 MB for non-partitioned table and 285.64 MB for the partitioned table

SELECT DISTINCT(VendorID) FROM `taxi_rides_ny.yellow_tripdata`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
-- 310.24 MB to process

SELECT DISTINCT(VendorID) FROM `taxi_rides_ny.partitioned_yellow_tripdata`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
-- 26.84 MB to process

-- **Answer** 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table

-- Question 7. External table storage
-- Where is the data stored in the External Table you created?
-- Options:
-- Big Query
-- Container Registry
-- GCP Bucket
-- Big Table

-- **Answer** GCP Bucket

-- Question 8. Clustering best practices
-- It is best practice in Big Query to always cluster your data:
-- Options:
-- True
-- False

-- **Answer** False
-- First of all, if the dataset size is small enough (1GB), there is no significant improvememnt.
-- Second, the clustering supports maximum 4 columns, if more are needed than rethink either the query either the data modeling.
-- Third, If the final result for a table (query results, business needs) don't involve any filtering, than there is no need for clustering.

-- Question 9. Understanding table scans
-- No Points: Write a SELECT count(*) query FROM the materialized table you created. How many bytes does it estimate will be read? Why?

SELECT COUNT(*) FROM `taxi_rides_ny.yellow_tripdata`;
-- 0 bytes to process
SELECT COUNT(*) FROM `taxi_rides_ny.external_yellow_tripdata`;
-- 0 bytes to process
SELECT COUNT(*) FROM `taxi_rides_ny.partitioned_yellow_tripdata`;
-- 0 bytes to process

SELECT COUNT(1) FROM `taxi_rides_ny.yellow_tripdata`;
-- 0 bytes to process

-- **Answer** 0 bytes to process. This is because BiqQuery uses table metadata information. The `Number of rows` in the Storage info.

-- ANSWERING TO HOMEWORK QUESTIONS IS DONE. DO MORE EXPLORATORY.
-- Next are some my personal investigations, not related to any question.

-- 1. What if selecting all between partitioned and non-partitioned tables?
SELECT * FROM `taxi_rides_ny.yellow_tripdata`;
-- 2.72 GB to process
SELECT * FROM `taxi_rides_ny.partitioned_yellow_tripdata`;
-- 2.72 GB to process
-- 1. There is no difference

-- 2. What if using more columns for a partitioned tables (columns not indicated in create table statment)? And also use the same query for non-partitioned tables, just for comparison.
SELECT DISTINCT(VendorID) FROM `taxi_rides_ny.yellow_tripdata`;
-- 155.12 MB to process

SELECT DISTINCT(VendorID) FROM `taxi_rides_ny.partitioned_yellow_tripdata`;
-- 155.12 MB to process
-- 2. So far no difference

-- adding filtering by clustered columns
SELECT DISTINCT(VendorID) FROM `taxi_rides_ny.partitioned_yellow_tripdata`
WHERE tpep_dropoff_datetime = '2024-03-01';
-- 1.79 MB to process
-- 2. This is a big improvement

SELECT DISTINCT(VendorID), tpep_dropoff_datetime FROM `taxi_rides_ny.partitioned_yellow_tripdata`
WHERE tpep_dropoff_datetime = '2024-03-01';
-- 1.79 MB to process

-- adding a second column in the query result, not related to clustering or partitioning
SELECT DISTINCT(VendorID), tip_amount FROM `taxi_rides_ny.yellow_tripdata`;
-- 310.24 MB to process

SELECT DISTINCT(VendorID), tip_amount FROM `taxi_rides_ny.partitioned_yellow_tripdata`
WHERE tpep_dropoff_datetime = '2024-03-01';
-- 2.68 MB to process
-- Still big improvment. Data quantity is added only for the other column, but preserving partitioned and clustered subsets.