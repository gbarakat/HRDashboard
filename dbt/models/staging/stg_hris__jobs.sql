with deduped as (
    {{ dedupe(source('raw', 'hris_jobs'), ['job_code']) }}
)
select
    job_code,
    job_title,
    job_family,
    grade_code                                 as grade,
    substring(grade_code from 2)::int          as grade_no,
    critical_role = 'Y'                        as is_critical_role
from deduped
