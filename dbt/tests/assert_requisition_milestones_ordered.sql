-- open <= screen <= offer <= accept <= start; filled requisitions have every milestone.
select req_id, status
from {{ ref('fact_requisition') }}
where screen_date < open_date
   or offer_date < screen_date
   or accept_date < offer_date
   or start_date < accept_date
   or (status = 'Filled' and (accept_date is null or start_date is null or hired_emp_id is null))
   or (status <> 'Filled' and hired_emp_id is not null)
