-- The person record's hire date must equal the HIRE row in job history; one hire per employee.
select p.emp_id, p.hire_date, count(h.emp_id) as hire_rows, min(h.effective_date) as hire_event_date
from {{ ref('stg_hris__persons') }} p
left join {{ ref('stg_hris__job_history') }} h on h.emp_id = p.emp_id and h.action_code = 'HIRE'
group by p.emp_id, p.hire_date
having count(h.emp_id) <> 1 or min(h.effective_date) <> p.hire_date
