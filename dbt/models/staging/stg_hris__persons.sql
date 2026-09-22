with deduped as (
    {{ dedupe(source('raw', 'hris_persons'), ['emp_id']) }}
)
select
    emp_id,
    case legal_sex when 'F' then 'Female' when 'M' then 'Male' end as gender,
    nationality,
    date_of_birth::date                        as birth_date,
    original_hire_date::date                   as hire_date,
    home_commute_km::numeric(6, 1)             as commute_km,
    fte::numeric(3, 2)                         as fte
from deduped
