-- 1

SELECT
  *
FROM
  `boreal-album-457603-u0.sales_dataset.sales_by_date_extended`
WHERE
  transaction_date BETWEEN DATE('2025-05-06') AND DATE('2025-05-07')


-- 2

SELECT
  region,
  SUM(amount) AS total_amount
FROM
  `boreal-album-457603-u0.sales_dataset.sales_by_date_extended`
WHERE
  transaction_date BETWEEN DATE('2025-05-01') AND DATE('2025-05-30')
GROUP BY
  region


--- 3
SELECT
  sales_channel,
  COUNT(*) AS transaction_count
FROM
  `boreal-album-457603-u0.sales_dataset.sales_by_date_extended`
WHERE
  transaction_date = DATE('2024-04-15')
GROUP BY
  sales_channel


--4
SELECT
  user_id,
  name,
  age
FROM
  `boreal-album-457603-u0.sales_dataset.user_by_age`
WHERE
  age < 25

-- 5
SELECT
  (FLOOR(age / 10) * 10) AS age_group,
  COUNT(user_id) AS user_count
FROM
  `boreal-album-457603-u0.sales_dataset.user_by_age`
GROUP BY
  age_group
ORDER BY
  age_group