# Module 1 Homework: Docker & SQL

### Question 1. Understanding Docker images

Run docker with the python:3.13 image. Use an entrypoint bash to interact with the container.

What's the version of pip in the image?

```bash
# run docker with python:3.13 image in interactive mode
docker run -it --rm python:3.13 bash
```

**Answer:** 25.3

### Question 2. Understanding Docker networking and docker-compose

Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?

**Answer:** postgres:5432

### Prepare the Data for the next questions

```bash
# Ingest green taxi data
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet

# Ingest taxi zone lookup data
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

### Question 3. Counting short trips

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a trip_distance of less than or equal to 1 mile?

```sql
SELECT COUNT(1)
FROM green_taxi_data_2025_11
WHERE (
        lpep_pickup_datetime >= '2025-11-01'
        AND lpep_dropoff_datetime < '2025-12-01'
    )
    AND trip_distance <= 1;
```

**Answer:** 8007

### Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles (to exclude data errors).

```sql
SELECT CAST(lpep_pickup_datetime AS DATE) AS day, MAX(trip_distance) AS max_trip_distance
FROM green_taxi_data_2025_11
WHERE
    trip_distance < 100
GROUP BY
    day
ORDER BY max_trip_distance DESC;
```

**Answer:** 2025-11-14

### Question 5. Biggest pickup zone

Which was the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025?

```sql
SELECT zpu."Zone", SUM(g.total_amount) AS total_amount
FROM
    green_taxi_data_2025_11 g
    JOIN taxi_zones_lookup zpu ON g."PULocationID" = zpu."LocationID"
WHERE
    CAST(lpep_pickup_datetime AS DATE) = '2025-11-18'
GROUP BY
    zpu."Zone"
ORDER BY total_amount DESC;
```

**Answer:** East Harlem North

### Question 6. Largest tip

For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip

```sql
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
```

**Answer:** Yorkville West

### Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:

    - Downloading the provider plugins and setting up backend,
    - Generating proposed changes and auto-executing the plan
    - Remove all resources managed by terraform`

**Answer:** terraform init, terraform apply -auto-approve, terraform destroy
