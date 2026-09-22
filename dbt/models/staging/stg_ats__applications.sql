with deduped as (
    {{ dedupe(source('raw', 'ats_applications'), ['application_id']) }}
)
select
    application_id,
    req_id,
    candidate_id,
    source_code,
    applied_on::date                           as applied_date,
    furthest_stage,
    case furthest_stage
        when 'APPLIED' then 1 when 'SCREENED' then 2 when 'INTERVIEWED' then 3
        when 'OFFERED' then 4 when 'HIRED' then 5
    end                                        as stage_reached,
    internal_emp_id,
    hired_emp_id
from deduped
