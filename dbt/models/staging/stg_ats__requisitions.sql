with deduped as (
    {{ dedupe(source('raw', 'ats_requisitions'), ['req_id']) }}
)
select
    req_id,
    team_code,
    job_code,
    opened_on::date                            as open_date,
    first_screen_on::date                      as screen_date,
    offer_on::date                             as offer_date,
    offer_accepted_on::date                    as accept_date,
    start_on::date                             as start_date,
    closed_on::date                            as closed_date,
    req_status                                 as status,
    fill_type,
    hire_source_code,
    hired_emp_id,
    requisition_ref,
    external_cost_usd::numeric(12, 2)          as external_cost_usd,
    recruiter_hours::numeric(6, 1)             as recruiter_hours
from deduped
