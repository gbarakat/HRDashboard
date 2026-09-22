-- Flattened 4-level hierarchy (division > department > section > team), effective-dated.
-- A team that changes division (the 2023 re-org) gets a new org_unit_key from the change date.
with ou as (
    select * from {{ ref('stg_hris__org_units') }}
),
current_position as (
    select team_code, division as current_division, department as current_department
    from ou
    where valid_to = date '9999-12-31'
)
select
    row_number() over (order by ou.team_code, ou.valid_from)::int as org_unit_key,
    ou.team_code,
    ou.team_name,
    ou.section,
    ou.department,
    ou.division,
    ou.station_code,
    cp.current_division,
    cp.current_department,
    ou.valid_from,
    ou.valid_to,
    ou.valid_to = date '9999-12-31'                                  as is_current
from ou
join current_position cp using (team_code)
