with deduped as (
    {{ dedupe(source('raw', 'hris_job_history'), ['emp_id', 'effective_date', 'action_code']) }}
)
select
    emp_id,
    effective_date::date                       as effective_date,
    action_code,
    action_reason,
    team_code,
    job_code,
    requisition_ref,
    term_type                                  as exit_type,
    case regret_flag when 'Y' then true when 'N' then false end as is_regretted,
    notice_date::date                          as notice_date
from deduped
