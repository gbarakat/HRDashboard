-- Input to ml/learner_segments.py: employees active at the end of the window,
-- with their training over the last 24 months split into elective categories.
with active as (
    select emp_id, employee_key, org_unit_key
    from {{ ref('fact_headcount_monthly') }}
    where month_end = '{{ var("window_end") }}'::date
),
t as (
    select f.emp_id, p.category, p.program_type, f.hours, f.cost_usd
    from {{ ref('fact_training') }} f
    join {{ ref('dim_program') }} p on p.program_key = f.program_key
    where f.completion_date > '{{ var("window_end") }}'::date - interval '24 months'
)
select
    a.employee_key,
    a.emp_id,
    a.org_unit_key,
    coalesce(sum(t.hours) filter (where t.program_type = 'Elective' and t.category = 'Technical'), 0)           as elective_technical_hours,
    coalesce(sum(t.hours) filter (where t.program_type = 'Elective' and t.category = 'Leadership'), 0)          as elective_leadership_hours,
    coalesce(sum(t.hours) filter (where t.program_type = 'Elective' and t.category = 'Digital'), 0)             as elective_digital_hours,
    coalesce(sum(t.hours) filter (where t.program_type = 'Elective' and t.category = 'Customer Service'), 0)    as elective_customer_hours,
    coalesce(sum(t.hours) filter (where t.program_type = 'Elective' and t.category = 'Safety & Compliance'), 0) as elective_safety_hours,
    coalesce(sum(t.hours) filter (where t.program_type = 'Mandatory'), 0)                                        as mandatory_hours,
    coalesce(sum(t.hours) filter (where t.program_type = 'Onboarding'), 0)                                       as onboarding_hours,
    count(t.hours) filter (where t.program_type = 'Elective')                                                    as elective_courses,
    coalesce(sum(t.hours), 0)                                                                                    as total_hours,
    coalesce(sum(t.cost_usd), 0)                                                                                 as total_cost_usd
from active a
left join t on t.emp_id = a.emp_id
group by a.employee_key, a.emp_id, a.org_unit_key
