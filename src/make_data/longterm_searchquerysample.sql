SELECT
  LOWER(hits.page.searchKeyword) as search_term
  ,CONCAT(CAST(fullVisitorId AS STRING), CAST(visitStartTime AS STRING)) AS session_id
  ,TIMESTAMP_SECONDS(visitStartTime+CAST(hits.time/1000 AS INT64)) as search_timestamp

FROM
  `govuk-bigquery-analytics.87773428.ga_sessions_*`,
  UNNEST(hits) AS hits
WHERE
  RIGHT(_table_suffix,2) = '01'
  AND hits.page.searchKeyword IS NOT NULL
  AND _table_suffix BETWEEN FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 24 MONTH))
    AND FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
