-- my_dbt_project/tests/no_negative_amount.sql

-- Test này kiểm tra không có đơn hàng nào có giá trị (amount) nhỏ hơn 0
-- Test FAIL nếu câu query này trả về bất kỳ dòng nào.

SELECT
    order_id,
    amount
FROM {{ ref('transformed_orders') }} -- Sử dụng ref() để tham chiếu đến model transformed_orders của bạn
WHERE amount < 0

