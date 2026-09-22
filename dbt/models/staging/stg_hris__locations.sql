with deduped as (
    {{ dedupe(source('raw', 'hris_locations'), ['station_code']) }}
)
select
    station_code,
    station_name,
    city,
    country,
    region,
    is_hub = 'Y'                               as is_hub
from deduped
