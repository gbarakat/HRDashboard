{#- Shared banding rules. Thresholds match generator/events.py so generator and warehouse agree. -#}
{% macro tenure_band(days_expr) -%}
    case
        when {{ days_expr }} < 183 then '0-6m'
        when {{ days_expr }} < 365 then '6-12m'
        when {{ days_expr }} < 730 then '1-2y'
        when {{ days_expr }} < 1826 then '2-5y'
        when {{ days_expr }} < 3652 then '5-10y'
        else '10y+'
    end
{%- endmacro %}

{% macro age_band(age_expr) -%}
    case
        when {{ age_expr }} < 25 then '<25'
        when {{ age_expr }} < 35 then '25-34'
        when {{ age_expr }} < 45 then '35-44'
        when {{ age_expr }} < 55 then '45-54'
        else '55+'
    end
{%- endmacro %}

{#- Whole months between two dates, like DATEDIF(..., "m"). -#}
{% macro months_between(start_expr, end_expr) -%}
    (extract(year from age({{ end_expr }}, {{ start_expr }})) * 12
     + extract(month from age({{ end_expr }}, {{ start_expr }})))::int
{%- endmacro %}

{% macro years_between(start_expr, end_expr) -%}
    extract(year from age({{ end_expr }}, {{ start_expr }}))::int
{%- endmacro %}

{#- Sort keys so Power BI orders the band labels correctly. -#}
{% macro tenure_band_sort(days_expr) -%}
    case
        when {{ days_expr }} < 183 then 1
        when {{ days_expr }} < 365 then 2
        when {{ days_expr }} < 730 then 3
        when {{ days_expr }} < 1826 then 4
        when {{ days_expr }} < 3652 then 5
        else 6
    end
{%- endmacro %}

{% macro age_band_sort(age_expr) -%}
    case
        when {{ age_expr }} < 25 then 1
        when {{ age_expr }} < 35 then 2
        when {{ age_expr }} < 45 then 3
        when {{ age_expr }} < 55 then 4
        else 5
    end
{%- endmacro %}
