--Gets search queries from gov.uk internal search over some date range

SELECT
  LOWER(hits.page.searchKeyword) as search_term
  ,CONCAT(CAST(fullVisitorId AS STRING), CAST(visitStartTime AS STRING)) AS session_id
  ,TIMESTAMP_SECONDS(visitStartTime+CAST(hits.time/1000 AS INT64)) as search_timestamp

FROM
  `govuk-bigquery-analytics.87773428.ga_sessions_*`,
  UNNEST(hits) AS hits
WHERE
  _table_suffix BETWEEN FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY))
                AND FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
  AND hits.page.searchKeyword IS NOT NULL
