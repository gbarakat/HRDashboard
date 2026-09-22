with days as (
    select d::date as date
    from generate_series('{{ var("calendar_start") }}'::date, '{{ var("calendar_end") }}'::date, interval '1 day') as g(d)
),
parts as (
    select
        date,
        extract(year from date)::int  as year,
        extract(month from date)::int as month_no
    from days
)
select
    to_char(date, 'YYYYMMDD')::int                                   as date_key,
    date,
    year,
    extract(quarter from date)::int                                  as quarter_no,
    'Q' || extract(quarter from date)::int                           as quarter,
    month_no,
    to_char(date, 'FMMonth')                                         as month_name,
    to_char(date, 'Mon')                                             as month_short,
    to_char(date, 'YYYY-MM')                                         as year_month,
    year * 100 + month_no                                            as year_month_no,
    date_trunc('month', date)::date                                  as month_start,
    (date_trunc('month', date) + interval '1 month - 1 day')::date   as month_end,
    date = (date_trunc('month', date) + interval '1 month - 1 day')::date as is_month_end,
    extract(isodow from date)::int                                   as day_of_week_no,
    to_char(date, 'FMDay')                                           as day_name,
    extract(isodow from date) in (6, 7)                              as is_weekend,
    -- fiscal year runs April to March and is named by its first year: FY2024/25 = Apr-2024 .. Mar-2025
    case when month_no >= 4 then year else year - 1 end              as fiscal_year_start,
    'FY' || (case when month_no >= 4 then year else year - 1 end)::text || '/'
        || right((case when month_no >= 4 then year + 1 else year end)::text, 2) as fiscal_year,
    ((month_no + 8) % 12) + 1                                        as fiscal_month_no,
    'FQ' || ((((month_no + 8) % 12)) / 3 + 1)::text                  as fiscal_quarter,
    date between '{{ var("window_start") }}'::date and '{{ var("window_end") }}'::date as is_in_reporting_window,
    date > '{{ var("window_end") }}'::date                           as is_forecast_horizon
from parts
