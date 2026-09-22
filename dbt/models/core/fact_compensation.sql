-- Grain: employee x annual pay review date (1 April), with the grade's pay band for that year.
with pay as (
    select * from {{ ref('stg_comp__salary_history') }}
)
select
    row_number() over (order by p.review_date, p.emp_id)::int       as compensation_key,
    p.pay_record_id,
    e.employee_key,
    p.emp_id,
    p.review_date                                                    as pay_review_date,
    extract(year from p.review_date)::int                            as review_year,
    ou.org_unit_key,
    j.job_key,
    l.location_key,
    p.grade,
    p.currency,
    p.base_salary,
    p.housing_allowance,
    p.transport_allowance,
    p.flying_allowance,
    p.housing_allowance + p.transport_allowance + p.flying_allowance as allowances,
    p.base_salary + p.housing_allowance + p.transport_allowance + p.flying_allowance as total_cash,
    b.band_min,
    b.band_mid,
    b.band_max,
    round(p.base_salary / b.band_mid, 4)                             as compa_ratio,
    round((p.base_salary - b.band_min) / nullif(b.band_max - b.band_min, 0), 4) as range_penetration
from pay p
join {{ ref('dim_employee') }} e
    on e.emp_id = p.emp_id and p.review_date between e.valid_from and e.valid_to
join {{ ref('dim_org_unit') }} ou
    on ou.team_code = e.team_code and p.review_date between ou.valid_from and ou.valid_to
join {{ ref('dim_job') }} j on j.job_code = e.job_code
join {{ ref('dim_location') }} l on l.station_code = ou.station_code
join {{ ref('stg_comp__pay_bands') }} b
    on b.grade = p.grade and b.band_year = extract(year from p.review_date)
