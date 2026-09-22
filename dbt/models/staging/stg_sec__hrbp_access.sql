with deduped as (
    {{ dedupe(source('raw', 'sec_hrbp_access'), ['user_email', 'division_name']) }}
)
select
    lower(user_email)                          as user_email,
    division_name                              as division
from deduped
