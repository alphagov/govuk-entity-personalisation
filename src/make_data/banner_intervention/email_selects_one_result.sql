/* This query extracts the total number and proportion of sessions that select the
   checker via email that selects at least one link on the results page
*/


DECLARE start_date STRING DEFAULT "20210803";
DECLARE end_date STRING DEFAULT "20210816";

CREATE OR REPLACE TABLE `govuk-bigquery-analytics.banner_intervention.email_one_result` AS

-- All distinct sessions that select the checker via the email

WITH
  sessions_email_select AS (
    SELECT DISTINCT
      CONCAT(fullVisitorId, "-", visitId) AS sessionId
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
    WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
      AND STARTS_WITH(hits.page.pagePath, "/next-steps-for-your-business?crn")
  ),

-- All distinct sessions that select the checker via the email that also selects
-- at least one results link on the results page

  sessions_email_results AS (
    SELECT DISTINCT
      CONCAT(fullVisitorId, "-", visitId) AS sessionId
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
    WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
    AND hits.eventInfo.eventCategory = 'SmartAnswerClicked'
    AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_email_select)
  )

-- The proportion of sessions that select the checker via the email that also
-- selects at least one results link on the results page

SELECT
  COUNT(sessionId) AS allSessionsThatSelectChecker,
  (SELECT COUNT(sessionId) FROM sessions_email_results) AS allSessionsThatAccessAtLeastOneResult,
  CAST (100 * (SELECT COUNT(sessionId) FROM sessions_email_results)/COUNT(sessionId) AS NUMERIC) AS proportionOfAllSessionsThatAccessAtLeastOneResult
FROM sessions_email_select
