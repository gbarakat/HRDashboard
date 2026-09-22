select
    row_number() over (order by course_code)::int                   as program_key,
    course_code,
    course_title,
    category,
    hours,
    cost_usd,
    is_mandatory,
    is_onboarding,
    case when is_mandatory then 'Mandatory' when is_onboarding then 'Onboarding' else 'Elective' end as program_type,
    mandatory_for,
    delivery_mode
from {{ ref('stg_lms__courses') }}
