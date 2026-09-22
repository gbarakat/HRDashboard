-- SCD Type 2. The HRIS provides effective-dated job history, so versions are derived from it
-- (a dbt snapshot is not needed). A new version opens on every hire, promotion, move or re-org.
with hist as (
    select * from {{ ref('stg_hris__job_history') }}
),
versions as (
    select
        emp_id,
        effective_date                                               as valid_from,
        action_code                                                  as change_action,
        action_reason                                                as change_reason,
        team_code,
        job_code,
        lead(effective_date) over (partition by emp_id order by effective_date) as next_valid_from
    from hist
    where action_code <> 'TERMINATION'
),
exits as (
    select emp_id, effective_date as exit_date, exit_type, is_regretted, notice_date
    from hist
    where action_code = 'TERMINATION'
),
persons as (
    select * from {{ ref('stg_hris__persons') }}
)
select
    row_number() over (order by v.emp_id, v.valid_from)::int        as employee_key,
    v.emp_id,
    p.gender,
    p.nationality,
    p.birth_date,
    p.hire_date,
    x.exit_date,
    x.exit_type,
    x.is_regretted                                                   as regretted_flag,
    x.notice_date,
    p.commute_km,
    p.commute_km > 30                                                as is_commute_over_30km,
    p.fte,
    v.team_code,
    v.job_code,
    v.change_action,
    v.change_reason,
    v.valid_from,
    coalesce(v.next_valid_from - 1, x.exit_date, date '9999-12-31') as valid_to,
    v.next_valid_from is null                                        as is_current,
    x.exit_date is null                                              as is_active
from versions v
join persons p using (emp_id)
left join exits x using (emp_id)
