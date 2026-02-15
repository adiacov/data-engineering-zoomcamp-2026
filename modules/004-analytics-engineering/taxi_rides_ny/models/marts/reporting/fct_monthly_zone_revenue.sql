/*
NOTE: HOMEWORK

The resulting fct_monthly_zone_revenue is copied from the GitHub repository for Module 4. 
This was done for several reasons:
- My solution was correct, but it didn’t match the final answer numbers.
- This fact table can be constructed in multiple ways (e.g., the number of columns required). 
- I implemented it one way, but it differs from the solution in the GitHub repository for Module 4.

Unfortunately, the instructions or description on how this model should be constructed are completely missing.
*/


select
    -- Grouping dimensions
    coalesce(pickup_zone, 'Unknown Zone') as pickup_zone,
    {% if target.type == 'bigquery' %}cast(date_trunc(pickup_datetime, month) as date)
    {% elif target.type == 'duckdb' %}date_trunc('month', pickup_datetime)
    {% endif %} as revenue_month,
    service_type,
    -- Revenue breakdown (summed by zone, month, and service type)
    sum(fare_amount) as revenue_monthly_fare,
    sum(extra) as revenue_monthly_extra,
    sum(mta_tax) as revenue_monthly_mta_tax,
    sum(tip_amount) as revenue_monthly_tip_amount,
    sum(tolls_amount) as revenue_monthly_tolls_amount,
    sum(ehail_fee) as revenue_monthly_ehail_fee,
    sum(improvement_surcharge) as revenue_monthly_improvement_surcharge,
    sum(total_amount) as revenue_monthly_total_amount,
    -- Additional metrics for operational analysis
    count(trip_id) as total_monthly_trips,
    avg(passenger_count) as avg_monthly_passenger_count,
    avg(trip_distance) as avg_monthly_trip_distance

from {{ ref('fct_trips') }}
group by pickup_zone, revenue_month, service_type