-- Each employee's versions must not overlap or leave gaps, and exactly one version is current.
with v as (
    select
        emp_id, employee_key, valid_from, valid_to, is_current,
        lead(valid_from) over (partition by emp_id order by valid_from) as next_from
    from {{ ref('dim_employee') }}
)
select emp_id, employee_key, 'gap or overlap' as problem
from v
where next_from is not null and next_from <> valid_to + 1
union all
select emp_id, null, 'valid_to before valid_from'
from v
where valid_to < valid_from
union all
select emp_id, null, 'not exactly one current version'
from v
group by emp_id
having count(*) filter (where is_current) <> 1
