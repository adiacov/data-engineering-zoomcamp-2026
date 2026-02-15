
with source as (
    select * from {{ source("dbt_raw_taxi_rides_ny", "dbt_fhv_tripdata") }}
),

renamed as (
    select
        cast(dispatching_base_num as string) as dispatching_base_num,
        cast(pickup_datetime as timestamp) as pickup_datetime,
        cast(dropOff_datetime as timestamp) as dropoff_datetime,
        cast(PUlocationID as integer) as pickup_location_id,
        cast(DOlocationID as integer) as dropoff_location_id,
        cast(SR_Flag as integer) as sr_flag,
        cast(Affiliated_base_number as string) as affiliated_base_number
    from source
    where dispatching_base_num is not null
)

select * from renamed