with deduped as (
    {{ dedupe(source('raw', 'hris_org_units'), ['team_code', 'effective_from']) }}
)
select
    team_code,
    team_name,
    section_name                               as section,
    department_name                            as department,
    division_name                              as division,
    station_code,
    effective_from::date                       as valid_from,
    coalesce(effective_to::date, date '9999-12-31') as valid_to
from deduped
