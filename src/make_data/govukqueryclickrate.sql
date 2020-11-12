SELECT
searchTerm,
link,
ROUND(AVG(linkPosition)) AS avg_rank,
COUNTIF(observationType = 'impression') AS views,
COUNTIF(observationType = 'click') AS clicks
FROM (
  SELECT
  customDimensions.value AS searchTerm,
  product.v2ProductName AS link,
  product.productListPosition AS linkPosition,
  CASE
      WHEN product.isImpression = true and product.isClick IS NULL THEN 'impression'
      WHEN product.isClick = true and product.isImpression IS NULL THEN 'click'
      ELSE NULL
  END AS observationType
  FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
  CROSS JOIN UNNEST(hits) AS hits
  CROSS JOIN UNNEST(hits.product) AS product
  CROSS JOIN UNNEST(product.customDimensions) AS customDimensions
  WHERE product.productListName = 'Search'
  AND _table_suffix BETWEEN FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY))
    AND FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
  AND product.productListPosition <= 20
  AND customDimensions.index = 71 -- has search term
) AS action
GROUP BY searchTerm, link
ORDER BY views desc
