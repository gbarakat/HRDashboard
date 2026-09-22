-- One population: every external hire in the window is the accepted candidate of a requisition.
select e.emp_id
from {{ ref('fact_employee_event') }} e
left join {{ ref('fact_requisition') }} r on r.hired_emp_id = e.emp_id and r.fill_type = 'External'
where e.event_type = 'Hire' and r.req_id is null
