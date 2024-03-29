/*
This script provides the number and proportion of sessions where the user has left
feedback about the quality of the results page of the checker, only if they have
accessed the checker via the Companies House email.

- The user replied to the feedback request at the bottom of a page: "Is this
  page useful? Yes/No"
- The feedback (recorded as an EVENT hit) is assigned to the corresponding pagePath
- "Feedback sessions" are sessions that start with pagePath = /next-steps-for-your-business/results
- (AND eventAction == "ffNoClick" OR "ffYesClick")

No requirements to run this script. Uses `govuk-bigquery-analytics.87773428.ga_sessions_*`
output table.
*/


DECLARE start_date STRING DEFAULT "20210803";
DECLARE end_date STRING DEFAULT "20210816";

CREATE OR REPLACE TABLE `govuk-bigquery-analytics.banner_intervention.email_feedback_results_page` AS

-- All sessions that access the checker via the email

WITH sessions_select_email AS (
  SELECT
    CONCAT(fullVisitorId, "-", visitId) AS sessionId
  FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
  CROSS JOIN UNNEST(hits) AS hits
  WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
  AND STARTS_WITH(hits.page.pagePath, "/next-steps-for-your-business?crn")
),

-- Count of all distinct sessions that access the checker via the email that also
-- get to the end of the checker (i.e. the results page). Needed for the final
-- output table to calculate the proportion of sessions that access the checker
-- results page and leave feedback

sessions_result_page AS (
  SELECT
    COUNT(DISTINCT CONCAT(fullVisitorId, "-", visitId)) AS totalSessionsThatAccessCheckerResults
  FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
  CROSS JOIN UNNEST(hits) AS hits
  WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
    AND STARTS_WITH(hits.page.pagePath, "/next-steps-for-your-business/results")
    AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_select_email)
),

-- All sessions that visit the checker results page and leave feedback
-- (eventAction = "ffNoClick" OR eventAction = "ffYesClick"), and sessionId matches
-- those sessionIds that access the checker via the email

sessions_feedback AS (
  SELECT
    CONCAT(fullVisitorId, "-", visitId) AS sessionId,
    hits.eventInfo.eventAction
  FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
  CROSS JOIN UNNEST(hits) AS hits
  WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
    AND STARTS_WITH(hits.page.pagePath, "/next-steps-for-your-business/results")
    AND hits.eventInfo.eventAction IN ("ffNoClick", "ffYesClick")
    AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_select_email)
)

-- Calculate proportion

SELECT
  eventAction,
  COUNT(DISTINCT sessionId) AS totalSessionsThatLeaveFeedback,
  (SELECT totalSessionsThatAccessCheckerResults FROM sessions_result_page) AS totalSessionsThatAccessCheckerResults,
  CAST (100 * COUNT(DISTINCT sessionId) / (SELECT totalSessionsThatAccessCheckerResults FROM sessions_result_page) AS NUMERIC) AS proportionOfSessionsThatAccessCheckerResultsAndLeaveFeedback
FROM sessions_feedback
GROUP BY eventAction
