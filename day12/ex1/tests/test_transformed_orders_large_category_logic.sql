-- my_new_dbt_project/tests/test_transformed_orders_large_category_logic.sql

-- Test FAIL nếu có đơn hàng nào được phân loại là 'large_order' nhưng amount <= 100

SELECT
    order_id,
    amount,
    order_category
FROM {{ ref('transformed_orders') }}
WHERE order_category = 'large_order'
  AND amount <= 100
