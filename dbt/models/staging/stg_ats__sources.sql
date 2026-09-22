with deduped as (
    {{ dedupe(source('raw', 'ats_sources'), ['source_code']) }}
)
select
    source_code,
    source_name                                as channel,
    source_type                                as channel_type
from deduped
