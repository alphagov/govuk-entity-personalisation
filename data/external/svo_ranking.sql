WITH cte_all AS
(
    SELECT
        TIMESTAMP_SECONDS(ga.visitStartTime) AS visitStartTime
        ,CAST(TIMESTAMP_SECONDS(ga.visitStartTime) AS DATE) AS visitStartDate
        ,hits.page.pagePath
        ,(SELECT value FROM hits.customDimensions WHERE index = 2) AS documentType
        ,hits.page.searchKeyword AS searchKeyword
        ,hits.page
    FROM
        `govuk-bigquery-analytics.87773428.ga_sessions_*` AS ga,
        UNNEST(hits) AS hits
    WHERE
        _table_suffix > FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR))
            AND hits.type = "PAGE"
),

cte_counts AS
(
    SELECT
        visitStartDate
        ,EXTRACT(WEEK FROM visitStartDate) AS visitStartDateWeek
        ,pagePath
        ,CASE
            WHEN documentType = 'simple_smart_answer' THEN 'smart_answers'
            WHEN searchKeyword IS NOT NULL THEN 'search'
            ELSE 'other'
            END AS pageType
        ,documentType
        ,searchKeyword
        ,COUNT(page) AS pageHits
    FROM cte_all
    GROUP BY
      visitStartDate
      ,pagePath
      ,documentType
      ,searchKeyword
),

cte_normalise AS
(
    SELECT
        visitStartDateWeek
        ,pagePath
        ,pageType
        ,documentType
        ,searchKeyword
        ,pageHits
        ,AVG(pageHits) OVER(PARTITION BY pagePath, pageType, documentType, searchKeyword ORDER BY visitStartDateWeek) AS pageHitsMean
        ,STDDEV_POP(pageHits) OVER(PARTITION BY pagePath, pageType, documentType, searchKeyword ORDER BY visitStartDateWeek) AS pageHitsSd
    FROM cte_counts
)

SELECT
    visitStartDateWeek
    ,pagePath
    ,pageType
    ,documentType
    ,searchKeyword
    ,pageHits
    ,pageHitsMean
    ,pageHitsSd
    ,(pageHits - pageHitsMean)/pageHitsSd AS pageNormalised
FROM cte_normalise;
