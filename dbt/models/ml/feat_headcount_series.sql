-- Input to ml/forecast.py: monthly headcount by team, restated to the CURRENT org structure
-- (teams moved by the 2023 re-org are counted in their new division for the whole history).
with hc as (
    select h.month_end, ou.team_code, count(*) as headcount
    from {{ ref('fact_headcount_monthly') }} h
    join {{ ref('dim_org_unit') }} ou on ou.org_unit_key = h.org_unit_key
    where h.month_end >= '{{ var("window_start") }}'::date
    group by 1, 2
),
flows as (
    select (date_trunc('month', event_date) + interval '1 month - 1 day')::date as month_end,
           count(*) filter (where event_type = 'Hire') as hires,
           count(*) filter (where event_type = 'Exit') as exits
    from {{ ref('fact_employee_event') }}
    group by 1
)
select
    hc.month_end,
    cur.org_unit_key                                                 as current_org_unit_key,
    hc.team_code,
    cur.division                                                     as current_division,
    hc.headcount,
    coalesce(f.hires, 0)                                             as company_hires,
    coalesce(f.exits, 0)                                             as company_exits
from hc
join {{ ref('dim_org_unit') }} cur on cur.team_code = hc.team_code and cur.is_current
left join flows f on f.month_end = hc.month_end
