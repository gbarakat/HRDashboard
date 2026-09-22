with deduped as (
    {{ dedupe(source('raw', 'perf_reviews'), ['review_id']) }}
)
select
    review_id,
    emp_id,
    review_year::int                           as review_year,
    review_date::date                          as review_date,
    rating::int                                as rating,
    potential::int                             as potential
from deduped
