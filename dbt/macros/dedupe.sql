{#- Keep the most recent extract of each business key (source re-extracts create exact duplicates). -#}
{% macro dedupe(relation, key_columns, order_by='extracted_at desc') -%}
    select * from (
        select src.*,
               row_number() over (partition by {{ key_columns | join(', ') }} order by {{ order_by }}) as _row_no
        from {{ relation }} as src
    ) ranked
    where _row_no = 1
{%- endmacro %}
