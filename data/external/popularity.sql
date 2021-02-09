WITH cte_all AS
(
    SELECT
        ga.date
        ,hits.page.pagePath
        ,(SELECT value FROM hits.customDimensions WHERE index = 2) AS documentType
        ,hits.page.searchKeyword AS searchKeyword
        ,hits.page
    FROM
        `govuk-bigquery-analytics.87773428.ga_sessions_*` AS ga,
        UNNEST(hits) AS hits
    WHERE
        _table_suffix > FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
            AND hits.type = "PAGE"
)

SELECT
    date
    ,CASE
        WHEN documentType = 'simple_smart_answer' THEN 'smart_answers'
        WHEN searchKeyword IS NOT NULL THEN 'search'
        ELSE pagePath
        END AS pageType
    ,documentType
    ,searchKeyword
    ,COUNT(page) AS pageHits
FROM cte_all
GROUP BY
  date
  ,pagePath
  ,documentType
  ,searchKeyword;
