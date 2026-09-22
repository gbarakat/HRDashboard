-- Input to ml/attrition.py: employees active at each 31-Dec snapshot, features known on that date,
-- and the outcome "voluntary exit within the next 12 months" (null for the latest snapshot).
with snapshots as (
    select date as snapshot_date
    from {{ ref('dim_date') }}
    where month_no = 12 and is_month_end
      and date between '{{ var("window_start") }}'::date and '{{ var("window_end") }}'::date
),
pop as (
    select s.snapshot_date, h.emp_id, h.employee_key, h.org_unit_key, h.job_key
    from snapshots s
    join {{ ref('fact_headcount_monthly') }} h on h.month_end = s.snapshot_date
),
training as (
    select p.snapshot_date, p.emp_id, sum(t.hours) as hours
    from pop p
    join {{ ref('fact_training') }} t
      on t.emp_id = p.emp_id
     and t.completion_date > p.snapshot_date - interval '12 months'
     and t.completion_date <= p.snapshot_date
    group by 1, 2
),
exits as (
    select emp_id, event_date, exit_type from {{ ref('fact_employee_event') }} where event_type = 'Exit'
)
select
    p.snapshot_date,
    p.emp_id,
    p.employee_key,
    p.org_unit_key,
    e.gender,
    j.job_family,
    j.grade_band,
    ou.division,
    p.snapshot_date - e.hire_date                                    as tenure_days,
    {{ tenure_band('p.snapshot_date - e.hire_date') }}               as tenure_band,
    {{ years_between('e.birth_date', 'p.snapshot_date') }}           as age_years,
    e.commute_km,
    coalesce(tr.hours, 0)                                            as training_hours_12m,
    pr.rating                                                        as last_rating,
    case when pr.rating is null then 'none' when pr.rating <= 2 then 'low'
         when pr.rating = 3 then 'mid' else 'high' end               as rating_band,
    case when p.snapshot_date = '{{ var("window_end") }}'::date then null
         else coalesce(x.exit_type = 'Voluntary' and x.event_date <= p.snapshot_date + interval '12 months', false)::int
    end                                                              as left_voluntary_12m
from pop p
join {{ ref('dim_employee') }} e on e.employee_key = p.employee_key
join {{ ref('dim_job') }} j on j.job_key = p.job_key
join {{ ref('dim_org_unit') }} ou on ou.org_unit_key = p.org_unit_key
left join training tr on tr.snapshot_date = p.snapshot_date and tr.emp_id = p.emp_id
left join {{ ref('fact_performance') }} pr
    on pr.emp_id = p.emp_id and pr.review_year = extract(year from p.snapshot_date)
left join exits x on x.emp_id = p.emp_id and x.event_date > p.snapshot_date
