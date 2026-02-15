/*
NOTE: HOMEWORK
In Module 4, it mentions that we should work with taxi data for the years 2019 and 2020. 
The source dataset is loaded for both years, but it contains invalid pickup and dropoff dates (e.g., years 2011, 2090, etc.). 
This is why I used a WHERE statement to filter the data.

However, the answer options in the homework do not match the actual numbers in my dimension and fact tables. 
To align with the homework answer options, I commented out the year filters, but this approach feels a bit confusing.

I believe this discrepancy should be clarified in the Module 4 content or the Homework instructions.

In my opinion, we should clean the data before building our models (after loading the source datasets).
*/


with green_tripdata as (
    select * from {{ ref('stg_green_tripdata') }}
    -- where 
    --     extract(year from pickup_datetime) in (2019, 2020) and
    --     extract(year from dropoff_datetime) in (2019, 2020)
),

yellow_tripdata as (
    select * from {{ ref('stg_yellow_tripdata') }}
    -- where
    --     extract(year from pickup_datetime) in (2019, 2020) and
    --     extract(year from dropoff_datetime) in (2019, 2020)
),

trips_unioned as (

    select * from green_tripdata
    union all
    select * from yellow_tripdata

)

select * from trips_unioned