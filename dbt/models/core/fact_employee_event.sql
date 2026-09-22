-- One row per hire, exit, move (lateral, internal requisition, re-org) or promotion in the reporting window.
with hist as (
    select
        h.*,
        lag(team_code) over w                                        as from_team_code,
        lag(job_code) over w                                         as from_job_code
    from {{ ref('stg_hris__job_history') }} h
    window w as (partition by emp_id order by effective_date,
                 case action_code when 'TERMINATION' then 2 else 1 end)
),
events as (
    select
        *,
        case action_code
            when 'HIRE' then 'Hire'
            when 'TERMINATION' then 'Exit'
            when 'PROMOTION' then 'Promotion'
            else 'Move'
        end                                                          as event_type,
        case action_code
            when 'TRANSFER' then 'Lateral'
            when 'INTERNAL_HIRE' then 'Internal requisition'
            when 'REORG' then 'Reorg'
        end                                                          as move_type
    from hist
    where effective_date between '{{ var("window_start") }}'::date and '{{ var("window_end") }}'::date
)
select
    row_number() over (order by e.effective_date, e.emp_id, e.action_code)::int as event_key,
    emp.employee_key,
    e.emp_id,
    e.effective_date                                                 as event_date,
    e.notice_date,
    e.event_type,
    e.move_type,
    e.exit_type,
    e.is_regretted,
    e.requisition_ref,
    ou.org_unit_key,
    fou.org_unit_key                                                 as from_org_unit_key,
    j.job_key,
    fj.job_key                                                       as from_job_key,
    l.location_key,
    j.grade_no - fj.grade_no                                         as grade_change,
    e.event_type = 'Hire'                                            as is_hire,
    e.event_type = 'Exit'                                            as is_exit,
    e.event_type in ('Promotion', 'Move') and j.grade_no > fj.grade_no as is_promotion,
    coalesce(e.move_type in ('Lateral', 'Internal requisition'), false) as is_internal_mobility,
    coalesce(e.exit_type = 'Voluntary', false)                       as is_voluntary_exit
from events e
join {{ ref('dim_employee') }} emp
    on emp.emp_id = e.emp_id and e.effective_date between emp.valid_from and emp.valid_to
join {{ ref('dim_org_unit') }} ou
    on ou.team_code = e.team_code and e.effective_date between ou.valid_from and ou.valid_to
left join {{ ref('dim_org_unit') }} fou
    on fou.team_code = e.from_team_code and e.effective_date - 1 between fou.valid_from and fou.valid_to
join {{ ref('dim_job') }} j on j.job_code = e.job_code
left join {{ ref('dim_job') }} fj on fj.job_code = e.from_job_code
join {{ ref('dim_location') }} l on l.station_code = ou.station_code
