-- Grain: employee x review year. Nine-box: performance band (rating) x potential.
with rev as (
    select
        r.*,
        case when r.rating <= 2 then 'Low' when r.rating = 3 then 'Moderate' else 'High' end as performance_band,
        case when r.rating <= 2 then 1 when r.rating = 3 then 2 else 3 end               as performance_band_no
    from {{ ref('stg_perf__reviews') }} r
)
select
    row_number() over (order by r.review_year, r.emp_id)::int       as performance_key,
    r.review_id,
    e.employee_key,
    r.emp_id,
    r.review_year,
    r.review_date,
    ou.org_unit_key,
    j.job_key,
    l.location_key,
    r.rating,
    r.potential,
    r.performance_band,
    (r.potential - 1) * 3 + r.performance_band_no                   as nine_box_cell,
    case (r.potential - 1) * 3 + r.performance_band_no
        when 1 then 'Underperformer'  when 2 then 'Effective'        when 3 then 'Trusted professional'
        when 4 then 'Dilemma'         when 5 then 'Core player'      when 6 then 'High performer'
        when 7 then 'Enigma'          when 8 then 'Growth employee'  when 9 then 'Future leader'
    end                                                              as nine_box_label
from rev r
join {{ ref('dim_employee') }} e
    on e.emp_id = r.emp_id and r.review_date between e.valid_from and e.valid_to
join {{ ref('dim_org_unit') }} ou
    on ou.team_code = e.team_code and r.review_date between ou.valid_from and ou.valid_to
join {{ ref('dim_job') }} j on j.job_code = e.job_code
join {{ ref('dim_location') }} l on l.station_code = ou.station_code
