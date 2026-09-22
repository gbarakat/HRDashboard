-- Grain: candidate x requisition, with the furthest funnel stage reached (1 Applied .. 5 Accepted).
with app as (
    select * from {{ ref('stg_ats__applications') }}
)
select
    row_number() over (order by a.applied_date, a.application_id)::int as application_key,
    a.application_id,
    r.requisition_key,
    a.req_id,
    c.channel_key,
    r.org_unit_key,
    r.job_key,
    r.location_key,
    a.applied_date,
    a.candidate_id,
    a.internal_emp_id is not null                                    as is_internal_candidate,
    a.stage_reached,
    case a.stage_reached
        when 1 then 'Applied' when 2 then 'Screened' when 3 then 'Interviewed'
        when 4 then 'Offered' when 5 then 'Accepted'
    end                                                              as stage_name,
    (a.stage_reached >= 2)::int                                      as reached_screen,
    (a.stage_reached >= 3)::int                                      as reached_interview,
    (a.stage_reached >= 4)::int                                      as reached_offer,
    (a.stage_reached = 5)::int                                       as accepted,
    a.hired_emp_id
from app a
join {{ ref('fact_requisition') }} r on r.req_id = a.req_id
join {{ ref('dim_channel') }} c on c.source_code = a.source_code
