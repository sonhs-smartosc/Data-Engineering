-- my_new_dbt_project/tests/test_transformed_orders_row_count_check.sql

-- Test FAIL nếu số dòng trong transformed_orders ít hơn 90% số dòng trong raw_data.orders
-- Ngưỡng 0.9 có thể điều chỉnh tùy logic lọc trong model transformed_orders.sql

WITH source_count AS (
    SELECT COUNT(*) AS total_rows
    FROM {{ source('raw_data', 'orders') }}
),

transformed_count AS (
    SELECT COUNT(*) AS total_rows
    FROM {{ ref('transformed_orders') }}
)

SELECT
    *
FROM transformed_count, source_count
WHERE transformed_count.total_rows < source_count.total_rows * 0.9 -- Ngưỡng kiểm tra
