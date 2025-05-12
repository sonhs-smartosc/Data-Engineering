-- my_new_dbt_project/models/example.sql

-- Đây là một model dbt đơn giản để chuyển đổi dữ liệu đơn hàng.
-- Nó chọn các cột cần thiết, thêm một cột tính toán và lọc dữ liệu.

SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    -- Tính toán cột mới, ví dụ: thêm 10% thuế
    amount * 1.10 AS amount_with_tax,
    -- Thêm một cột phân loại đơn hàng dựa trên giá trị
    CASE
        WHEN amount > 100 THEN 'large_order'
        ELSE 'small_order'
    END AS order_category,
    'processed' AS processing_status -- Thêm một cột cố định

FROM
    {{ source('raw_data', 'orders') }} -- Tham chiếu đến bảng nguồn thô, ví dụ: {{ source('raw_data', 'orders') }}

WHERE
    -- Lọc các đơn hàng có giá trị lớn hơn 0
    amount > 0
    -- Bạn có thể thêm các điều kiện lọc khác, ví dụ theo ngày
    -- AND order_date >= '2023-01-01'
