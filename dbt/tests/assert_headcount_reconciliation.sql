-- Rule: headcount(m) = headcount(m-1) + hires(m) - exits(m) for every month of the window.
-- Headcount comes from fact_headcount_monthly (built from SCD2 versions); hires and exits
-- come from fact_employee_event (built from events). Also fails if any of the 96 months is missing.
with hc as (
    select month_end, count(*) as headcount
    from {{ ref('fact_headcount_monthly') }}
    group by month_end
),
flows as (
    select
        (date_trunc('month', event_date) + interval '1 month - 1 day')::date as month_end,
        count(*) filter (where event_type = 'Hire') as hires,
        count(*) filter (where event_type = 'Exit') as exits
    from {{ ref('fact_employee_event') }}
    group by 1
),
months as (
    select date as month_end
    from {{ ref('dim_date') }}
    where is_month_end and is_in_reporting_window
),
recon as (
    select
        m.month_end,
        prev.headcount                                               as opening,
        coalesce(f.hires, 0)                                         as hires,
        coalesce(f.exits, 0)                                         as exits,
        cur.headcount                                                as closing,
        prev.headcount + coalesce(f.hires, 0) - coalesce(f.exits, 0) - cur.headcount as difference
    from months m
    left join hc cur on cur.month_end = m.month_end
    left join hc prev on prev.month_end = (date_trunc('month', m.month_end) - interval '1 day')::date
    left join flows f on f.month_end = m.month_end
)
select * from recon
where difference is distinct from 0
union all
select null, null, null, null, null, count(*) - 96
from recon
having count(*) <> 96
