with deduped as (
    {{ dedupe(source('raw', 'lms_completions'), ['completion_id']) }}
)
select
    completion_id,
    emp_id,
    course_code,
    completion_date::date                      as completion_date,
    hours::numeric(6, 1)                       as hours,
    cost_usd::numeric(12, 2)                   as cost_usd
from deduped
