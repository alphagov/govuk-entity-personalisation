/* This query extracts the total number and proportion of sessions that access the
   checker via the banner intervention that access the results page
*/


DECLARE start_date STRING DEFAULT "20210803";
DECLARE end_date STRING DEFAULT "20210816";

CREATE OR REPLACE TABLE `govuk-bigquery-analytics.banner_intervention.banner_results_page` AS

-- All distinct sessions that select the checker via the banner (eventAction =
-- interventionClicked)

WITH
  sessions_select_banner AS (
    SELECT DISTINCT
      CONCAT(fullVisitorId, "-", visitId) AS sessionId
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
    WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
      AND hits.eventInfo.eventCategory = 'interventionBanner'
      AND hits.eventInfo.eventAction = 'interventionClicked'
  ),

-- All sessions that select the checker via the banner that also get to the end
-- of the checker (i.e. the results page)

  sessions_results_page AS (
    SELECT
      CONCAT(fullVisitorId, "-", visitId) AS sessionId
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
    WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
      AND STARTS_WITH(hits.page.pagePath, "/next-steps-for-your-business/results")
      AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_select_banner)
  )

-- The proportion of sessions that access the checker via the banner that also
-- get to the end of the checker (i.e. the results page)

SELECT
  COUNT(DISTINCT sessionId) AS allSessionsThatSelectChecker,
  (SELECT COUNT(DISTINCT sessionId) FROM sessions_results_page) AS allSessionsThatAccessResultsPage,
  CAST (100 * (SELECT COUNT(DISTINCT sessionId) FROM sessions_results_page)/COUNT(DISTINCT sessionId) AS NUMERIC) AS proportionOfAllSessionsThatAccessResultsPage
FROM sessions_select_banner
