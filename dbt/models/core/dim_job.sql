select
    row_number() over (order by grade_no, job_family, job_code)::int as job_key,
    job_code,
    job_title,
    job_family,
    grade,
    grade_no,
    case when grade_no <= 4 then 'G1-G4' when grade_no <= 8 then 'G5-G8' else 'G9-G12' end as grade_band,
    is_critical_role                                                 as critical_role_flag
from {{ ref('stg_hris__jobs') }}
