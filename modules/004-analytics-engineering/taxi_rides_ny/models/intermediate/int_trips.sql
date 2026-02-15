/*
- Enrich and deduplicate trip data
- Demonstrates enrichment and surrogate key generation
- Data quality analysis available in analyses/trips_data_quality.sql
*/


with unioned as (
    select * from {{ref('int_trips_unioned')}}
),

payments as (
    select * from {{ref('dim_payments')}}
),

cleaned_and_enriched as (

    select
        -- generate unique trip identifier (surrogate key)
        {{
            dbt_utils.generate_surrogate_key([
                'u.vendor_id',
                'u.pickup_datetime',
                'u.pickup_location_id',
                'u.service_type'
            ])
        }} as trip_id
        -- Identifiers
        , u.vendor_id
        , u.rate_code_id
        , u.service_type
        -- Timestamps
        , u.pickup_datetime
        , u.dropoff_datetime
        -- Locations
        , u.pickup_location_id
        , u.dropoff_location_id
        -- Trip details
        , u.passenger_count
        , u.trip_distance
        , u.trip_type
        , u.store_and_fwd_flag
        -- Trip duration
        -- duration in seconds / minutes
        , {{ dbt.datediff('u.pickup_datetime', 'u.dropoff_datetime', 'second') }} as trip_seconds
        , {{ dbt.datediff('u.pickup_datetime', 'u.dropoff_datetime', 'second') }} / 60.0 as trip_minutes
        -- Money fields converted (uses project macro dispatch)
        , {{ cents_to_dollars('u.fare_amount') }} as fare_amount
        , {{ cents_to_dollars('u.extra') }} as extra
        , {{ cents_to_dollars('u.mta_tax') }} as mta_tax
        , {{ cents_to_dollars('u.tip_amount') }} as tip_amount
        , {{ cents_to_dollars('u.tolls_amount') }} as tolls_amount
        , {{ cents_to_dollars('u.improvement_surcharge') }} as improvement_surcharge
        , {{ cents_to_dollars('u.total_amount') }} as total_amount
        , u.payment_type
        , {{ get_payment_description('u.payment_type') }}
        , u.ehail_fee
        -- simple data quality flag
        , case
                when u.pickup_datetime is null or u.dropoff_datetime is null then false
                when {{ dbt.datediff('u.pickup_datetime', 'u.dropoff_datetime', 'second') }} <= 0 then false
                when coalesce(u.trip_distance, 0) <= 0 then false
                else true
            end as is_valid
    from unioned u
    left join payments pt
        on coalesce(u.payment_type, 5) = pt.payment_type

),

-- Deduplicate: if multiple trips match (same vendor, second, location, service), keep first
ranked as (
    select *, row_number() over (
            partition by
                vendor_id, pickup_datetime, pickup_location_id, trip_type
            order by dropoff_datetime
        ) as row_num
    from cleaned_and_enriched
),
final as (
    select *
    from ranked
    where
        row_num = 1
)

select * from final