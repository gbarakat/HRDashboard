-- Grain: employee x month end. Includes 2017-12-31 as the opening balance for January 2018.
-- An employee counts at a month end if hired on/before it and not exited on/before it.
with months as (
    select date as month_end, month_start
    from {{ ref('dim_date') }}
    where is_month_end
      and date between '{{ var("window_start") }}'::date - 1 and '{{ var("window_end") }}'::date
),
emp as (
    select * from {{ ref('dim_employee') }}
)
select
    m.month_end,
    e.emp_id,
    e.employee_key,
    ou.org_unit_key,
    j.job_key,
    l.location_key,
    e.fte,
    1                                                                as headcount,
    e.hire_date between m.month_start and m.month_end                as is_hired_in_month,
    {{ months_between('e.hire_date', 'm.month_end') }}              as tenure_months,
    {{ tenure_band('m.month_end - e.hire_date') }}                   as tenure_band,
    {{ years_between('e.birth_date', 'm.month_end') }}               as age_years,
    {{ age_band(years_between('e.birth_date', 'm.month_end')) }}     as age_band
from months m
join emp e
    on m.month_end between e.valid_from and e.valid_to
   and e.hire_date <= m.month_end
   and (e.exit_date is null or e.exit_date > m.month_end)
join {{ ref('dim_org_unit') }} ou
    on ou.team_code = e.team_code and m.month_end between ou.valid_from and ou.valid_to
join {{ ref('dim_job') }} j on j.job_code = e.job_code
join {{ ref('dim_location') }} l on l.station_code = ou.station_code
