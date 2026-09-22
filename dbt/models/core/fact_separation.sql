{{ config(materialized='view') }}
-- One row per exit: a view over fact_employee_event with tenure and profile at exit.
with exits as (
    select * from {{ ref('fact_employee_event') }} where event_type = 'Exit'
),
emp as (
    select * from {{ ref('dim_employee') }}
)
select
    x.event_key                                                      as separation_key,
    x.employee_key,
    x.emp_id,
    x.event_date                                                     as exit_date,
    x.notice_date,
    e.hire_date,
    x.exit_type,
    x.is_regretted,
    x.is_voluntary_exit,
    x.org_unit_key,
    x.job_key,
    x.location_key,
    x.event_date - e.hire_date                                       as tenure_days,
    {{ months_between('e.hire_date', 'x.event_date') }}              as tenure_months,
    {{ tenure_band('x.event_date - e.hire_date') }}                  as tenure_band,
    {{ months_between('e.hire_date', 'x.event_date') }} < 12         as is_first_year_exit,
    {{ years_between('e.birth_date', 'x.event_date') }}              as age_at_exit,
    last_review.rating                                               as last_rating
from exits x
join emp e on e.employee_key = x.employee_key
left join lateral (
    select r.rating
    from {{ ref('stg_perf__reviews') }} r
    where r.emp_id = x.emp_id and r.review_date <= x.event_date
    order by r.review_date desc
    limit 1
) last_review on true
