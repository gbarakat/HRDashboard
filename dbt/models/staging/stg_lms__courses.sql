with deduped as (
    {{ dedupe(source('raw', 'lms_courses'), ['course_code']) }}
)
select
    course_code,
    course_title,
    category,
    duration_hours::numeric(6, 1)              as hours,
    cost_usd::numeric(12, 2)                   as cost_usd,
    mandatory_for,
    mandatory_for is not null and mandatory_for <> 'ONBOARDING' as is_mandatory,
    mandatory_for = 'ONBOARDING'               as is_onboarding,
    delivery_mode
from deduped
