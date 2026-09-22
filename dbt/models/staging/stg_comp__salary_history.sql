with deduped as (
    {{ dedupe(source('raw', 'comp_salary_history'), ['pay_record_id']) }}
)
select
    pay_record_id,
    emp_id,
    review_date::date                          as review_date,
    grade_code                                 as grade,
    currency,
    base_annual::numeric(12, 2)                as base_salary,
    housing_allowance::numeric(12, 2)          as housing_allowance,
    transport_allowance::numeric(12, 2)        as transport_allowance,
    flying_allowance::numeric(12, 2)           as flying_allowance,
    change_reason
from deduped
