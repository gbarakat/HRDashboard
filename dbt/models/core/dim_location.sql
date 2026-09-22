select
    row_number() over (order by is_hub desc, station_code)::int     as location_key,
    station_code,
    station_name,
    city,
    country,
    region,
    is_hub
from {{ ref('stg_hris__locations') }}
