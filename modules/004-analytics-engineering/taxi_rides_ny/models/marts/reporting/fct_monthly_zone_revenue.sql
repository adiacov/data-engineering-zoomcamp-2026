
with trips_unioned as (
    select * from {{ ref("int_trips_unioned") }}
),

transformed as (
    select 
        pickup_location_id,
        extract(year from pickup_datetime) as year,
        extract(month from pickup_datetime) as month,
        total_amount
    from trips_unioned
),

zones as (
    select * from {{ ref("dim_zones") }}
),

final as (
    select 
        zone,
        year,
        month,
        sum(total_amount) as monthly_amount
    from transformed t 
    join zones z on t.pickup_location_id = z.location_id
    group by zone, year, month
    order by zone, year, month
)

select * from final

/*

what is fct_monthly_zone_revenue
- zone
- month
- year (???) - yes because there are 2 same months for 2019 and 2020
- revenue -> total_amount (?)

Grain?
- one row is a total_revenue per month for a zone

Thinking:
A zone may have OR may not have a revenue for a certain month.
If a zone has a revenue in a certain month it's the aggregated sum of total_amount ????

*/