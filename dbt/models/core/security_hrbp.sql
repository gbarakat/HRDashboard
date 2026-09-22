-- Row-level security mapping for the Power BI HRBP role: user_email -> division.
select user_email, division
from {{ ref('stg_sec__hrbp_access') }}
