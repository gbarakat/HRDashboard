-- Every fact row must point at the employee version that was valid on the fact's date.
with checks as (
    select 'headcount' as fact, f.employee_key, f.month_end as fact_date from {{ ref('fact_headcount_monthly') }} f
    union all
    select 'event', f.employee_key, f.event_date from {{ ref('fact_employee_event') }} f
    union all
    select 'compensation', f.employee_key, f.pay_review_date from {{ ref('fact_compensation') }} f
    union all
    select 'performance', f.employee_key, f.review_date from {{ ref('fact_performance') }} f
    union all
    select 'training', f.employee_key, f.completion_date from {{ ref('fact_training') }} f
)
select c.*
from checks c
join {{ ref('dim_employee') }} e on e.employee_key = c.employee_key
where c.fact_date not between e.valid_from and e.valid_to
