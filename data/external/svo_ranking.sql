/* Normalised Weekly Page Hits */
-- Get normalised weekly page hits using min-max normalisation.

--  ---------
--  Explainer
--  ---------
--  - Weekly to account for differences in daily and weekly traffic.
--  - This is chosen so we can get popularity scores in the interval [0, 1].
--  - We normalise to keep memory consumption low whilst retaining a ranking.
--  - We use min-max normalisation for the intuitiveness of page hits with values closer to
--      0 meaning they are less popular compared to pages with values closer to 1.
--  To define our thinking/logic for the SQL, we define the following:
--      x:      weekly page hits for each page
--      group:  all pages per week

-- -------
-- Example
-- -------
-- The intention is to get a table like below:

/*
date | dateWeek | page | pageHits | pageHitsMax | pageHitsMin |
| --- | --- | --- | --- | --- | --- |
| 2021-01-01 | 1 | a | *12* | **56** | *12* |
| 2021-01-02 | 1 | b | **56** | **56** | *12* |
| 2021-01-06 | 1 | c | 23 | **56** | *12* |
| 2021-01-09 | 2 | b | 54 | **87** | *46* |
| 2021-01-13 | 2 | c | **87** | **87** | *46* |
| 2021-01-14 | 2 | a | *46* | **87** | *46* |
*/

--  ------------------
--  Structure of query
--  ------------------
--  1.  Get relevant columns, `cte_all`.
--          Includes transforming integer column to timestamp
--  2.  Create id column, `cte_id`.
--          This involves identifying normal pages (as defined by pagePath) from 'smart_answers' and
--          'search' (as defined by other criteria)
--  3.  Compute counts of page hits by week, `cte_week_counts`.
--          We do it by week so we can account for the differences in weekday and weekend traffic together.
--  4.  Compute the max and min page hits for all pages for each week, `cte_normalise`
--          This is so we can normalise each page's page hits for each week
--  5.  Compute the min-max normalised page hits for each page per week.

--  ----------
--  References
--  ----------
--  Use `SAFE_DIVIDE()` to handle division by 0 or NULL:
--  https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-and-operators#mathematical-functions
--  Also considered z-score standardisation:
--  https://www.investopedia.com/terms/z/zscore.asp#:~:text=A%20Z%2Dscore%20is%20a,identical%20to%20the%20mean%20score

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

cte_id AS
(
    SELECT
        visitStartTime
        ,visitStartDate
        ,EXTRACT(WEEK FROM visitStartDate) AS visitStartDateWeek
        ,CASE
            WHEN documentType = 'simple_smart_answer' THEN CONCAT('smart answers - ', pagePath)
            WHEN searchKeyword IS NOT NULL THEN CONCAT('search - ', pagePath)
            ELSE CONCAT('other - ', pagePath)
            END AS pageId
        ,page
    FROM cte_all
),

cte_week_counts AS
(
    SELECT
        visitStartDate
        ,visitStartDateWeek
        ,pageId
        ,COUNT(page) AS pageHits
    FROM cte_id
    GROUP BY
        visitStartDateWeek
        ,pageId
),

cte_normalise AS
(
    SELECT
        visitStartDate
        ,visitStartDateWeek
        ,pageId
        ,pageHits
        ,MAX(pageHits) OVER(PARTITION BY visitStartDateWeek) AS pageHitsMax
        ,MIN(pageHits) OVER(PARTITION BY visitStartDateWeek) AS pageHitsMin
    FROM cte_week_counts
)

SELECT
    visitStartDateWeek
    ,pageId
    ,pageHits
    ,pageHitsMin
    ,pageHitsMax
    ,SAFE_DIVIDE((pageHits - pageHitsMin), (pageHitsMax - pageHitsMin)) AS pageHitsNormalised
FROM cte_normalise;
