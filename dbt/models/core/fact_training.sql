-- Grain: employee x program x completion date.
with c as (
    select * from {{ ref('stg_lms__completions') }}
)
select
    row_number() over (order by c.completion_date, c.completion_id)::int as training_key,
    c.completion_id,
    e.employee_key,
    c.emp_id,
    p.program_key,
    c.completion_date,
    ou.org_unit_key,
    j.job_key,
    l.location_key,
    c.hours,
    c.cost_usd
from c
join {{ ref('dim_program') }} p on p.course_code = c.course_code
join {{ ref('dim_employee') }} e
    on e.emp_id = c.emp_id and c.completion_date between e.valid_from and e.valid_to
join {{ ref('dim_org_unit') }} ou
    on ou.team_code = e.team_code and c.completion_date between ou.valid_from and ou.valid_to
join {{ ref('dim_job') }} j on j.job_code = e.job_code
join {{ ref('dim_location') }} l on l.station_code = ou.station_code
