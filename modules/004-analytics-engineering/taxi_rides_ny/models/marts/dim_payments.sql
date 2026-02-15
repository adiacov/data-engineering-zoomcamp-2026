with payments as (
    select
        distinct(payment_type) as payment_type,
        {{ get_payment_description('payment_type') }},
    from {{ ref('int_trips_unioned') }}
    order by payment_type
)

select * from payments