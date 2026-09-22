-- An exit must be the last event of an employee and cannot precede the hire.
select h.emp_id
from {{ ref('stg_hris__job_history') }} h
join {{ ref('stg_hris__job_history') }} x on x.emp_id = h.emp_id and x.action_code = 'TERMINATION'
where h.action_code <> 'TERMINATION' and h.effective_date > x.effective_date
