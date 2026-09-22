-- Input to ml/pay_equity.py: one row per employee per pay review with the legitimate pay factors.
select
    c.compensation_key,
    c.employee_key,
    c.emp_id,
    c.org_unit_key,
    c.pay_review_date,
    c.review_year,
    (e.gender = 'Female')::int                                       as is_female,
    j.grade,
    j.job_family,
    l.station_code,
    round((c.pay_review_date - e.hire_date) / 365.25, 4)             as tenure_years,
    pr.rating                                                        as prior_year_rating,
    c.base_salary,
    c.compa_ratio
from {{ ref('fact_compensation') }} c
join {{ ref('dim_employee') }} e on e.employee_key = c.employee_key
join {{ ref('dim_job') }} j on j.job_key = c.job_key
join {{ ref('dim_location') }} l on l.location_key = c.location_key
left join {{ ref('fact_performance') }} pr
    on pr.emp_id = c.emp_id and pr.review_year = c.review_year - 1
