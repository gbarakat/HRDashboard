-- Each filled requisition has exactly one accepted application, and it is the hired person.
select r.req_id, count(a.application_key) as accepted_applications
from {{ ref('fact_requisition') }} r
left join {{ ref('fact_application') }} a on a.requisition_key = r.requisition_key and a.accepted = 1
where r.status = 'Filled'
group by r.req_id, r.hired_emp_id
having count(a.application_key) <> 1 or max(a.hired_emp_id) is distinct from r.hired_emp_id
