
with source as (
    select * from {{ source("dbt_raw_taxi_rides_ny", "dbt_yellow_tripdata") }}
),

renamed as (
    select
        -- identifiers
        cast(VendorID as integer) as vendor_id,
        cast(RatecodeID as integer) as rate_code_id,
        cast(PULocationID as integer) as pickup_location_id,
        cast(DOLocationID as integer) as dropoff_location_id,
        -- timestamps
        cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
        cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
        -- trip info
        cast(store_and_fwd_flag as string) as store_and_fwd_flag,
        cast(passenger_count as integer) as passenger_count,
        cast(trip_distance as numeric) as trip_distance,
        1 as trip_type, -- prepare for union with green_tripdata. yellow taxis can only be street-hail (trip_type=1)
        -- payment info
        cast(fare_amount as numeric) as fare_amount,
        cast(extra as numeric) as extra,
        cast(mta_tax as numeric) as mta_tax,
        cast(tip_amount as numeric) as tip_amount,
        cast(tolls_amount as numeric) as tolls_amount,
        cast(improvement_surcharge as numeric) as improvement_surcharge,
        cast(total_amount as numeric) as total_amount,
        cast(payment_type as integer) as payment_type,
        0 as ehail_fee, -- prepare for union with green_tripdata. yellow taxi do not have ehail fees
        'Yellow' as service_type,
    from source
    -- Filter out records with null vendorID
    where VendorID is not null
),

final as (
    select * from renamed
    -- Limit the result for DEV environment (1 month)
    {% if target.name == 'dev' %}
    where pickup_datetime >= '2019-01-01' and pickup_datetime <= '2019-02-01'
    {% endif %}
)

select * from final