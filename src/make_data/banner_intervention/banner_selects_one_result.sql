/* This query extracts the total number and proportion of sessions that selects
   the checker via the banner intervention that also select at least one link on
   the results page
*/


DECLARE start_date STRING DEFAULT "20210803";
DECLARE end_date STRING DEFAULT "20210816";

CREATE OR REPLACE TABLE `govuk-bigquery-analytics.banner_intervention.banner_one_result` AS

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

-- All distinct sessions that access the checker via the banner that also selects
-- at least one results link on the results page

  sessions_select_result AS (
    SELECT DISTINCT
      CONCAT(fullVisitorId, "-", visitId) AS sessionId
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
    WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
    AND hits.eventInfo.eventCategory = 'SmartAnswerClicked'
    AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_select_banner)
  )

-- The proportion of sessions that access the checker via the banner that also
-- selects at least one results link on the results page

SELECT
  COUNT(sessionId) AS allSessionsThatSelectChecker,
  (SELECT COUNT(sessionId) FROM sessions_select_result) AS allSessionsThatAccessAtLeastOneResult,
  CAST (100 * (SELECT COUNT(sessionId) FROM sessions_select_result)/COUNT(sessionId) AS NUMERIC) AS proportionOfAllSessionsThatAccessAtLeastOneResult
FROM sessions_select_banner
