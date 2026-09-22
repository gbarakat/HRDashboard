with deduped as (
    {{ dedupe(source('raw', 'comp_pay_bands'), ['grade_code', 'band_year']) }}
)
select
    grade_code                                 as grade,
    band_year::int                             as band_year,
    band_min::numeric(12, 2)                   as band_min,
    band_mid::numeric(12, 2)                   as band_mid,
    band_max::numeric(12, 2)                   as band_max,
    currency
from deduped
