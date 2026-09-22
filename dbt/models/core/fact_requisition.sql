-- Accumulating snapshot: one row per requisition with its milestone dates.
with req as (
    select * from {{ ref('stg_ats__requisitions') }}
)
select
    row_number() over (order by r.open_date, r.req_id)::int         as requisition_key,
    r.req_id,
    ou.org_unit_key,
    j.job_key,
    l.location_key,
    c.channel_key,
    r.open_date,
    r.screen_date,
    r.offer_date,
    r.accept_date,
    r.start_date,
    r.closed_date,
    r.status,
    r.fill_type,
    r.hired_emp_id,
    he.employee_key                                                  as hired_employee_key,
    r.accept_date - r.open_date                                      as days_to_fill,
    r.start_date - r.open_date                                       as days_to_start,
    r.external_cost_usd,
    r.recruiter_hours,
    r.recruiter_hours * {{ var('recruiter_hourly_cost') }}           as internal_cost_usd,
    r.external_cost_usd + r.recruiter_hours * {{ var('recruiter_hourly_cost') }} as total_cost_usd,
    r.status = 'Filled'                                              as is_filled,
    coalesce(r.fill_type = 'Internal', false)                        as is_internal_fill,
    coalesce(r.fill_type = 'External', false)                        as is_external_hire
from req r
join {{ ref('dim_org_unit') }} ou
    on ou.team_code = r.team_code and r.open_date between ou.valid_from and ou.valid_to
join {{ ref('dim_job') }} j on j.job_code = r.job_code
join {{ ref('dim_location') }} l on l.station_code = ou.station_code
left join {{ ref('dim_channel') }} c on c.source_code = r.hire_source_code
left join {{ ref('dim_employee') }} he
    on he.emp_id = r.hired_emp_id and r.start_date between he.valid_from and he.valid_to
