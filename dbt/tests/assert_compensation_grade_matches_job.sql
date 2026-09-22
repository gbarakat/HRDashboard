-- The grade on the pay record equals the grade of the job held on the review date.
select c.pay_record_id, c.grade, j.grade as job_grade
from {{ ref('fact_compensation') }} c
join {{ ref('dim_job') }} j on j.job_key = c.job_key
where c.grade <> j.grade
