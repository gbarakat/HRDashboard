select
    row_number() over (order by case channel_type when 'Internal' then 0 else 1 end, source_code)::int as channel_key,
    source_code,
    channel,
    channel_type
from {{ ref('stg_ats__sources') }}
