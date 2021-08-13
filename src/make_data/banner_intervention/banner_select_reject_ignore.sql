/* This query extracts the total number and proportion of sessions that select the
   checker via the banner intervention, reject the checker via the banner
   intervention, and that ignore the checker via the banner intervention.
*/


DECLARE start_date STRING DEFAULT "20210803";
DECLARE end_date STRING DEFAULT "20210816";

CREATE OR REPLACE TABLE `govuk-bigquery-analytics.banner_intervention.banner_select_reject_ignore` AS

-- All sessions that are shown the checker via the banner (eventCategory =
-- interventionBanner)

WITH
  sessions_next_steps AS (
    SELECT DISTINCT
      CONCAT(fullVisitorId, "-", visitId) AS sessionId,
      hits.eventInfo.eventAction
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
    WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
      AND hits.eventInfo.eventCategory = 'interventionBanner'
  ),

-- All distinct sessions that are shown the banner (eventCategory = interventionBanner;
-- eventAction = interventionShown)

  sessions_next_steps_shown AS (
    SELECT DISTINCT
      sessionId
    FROM sessions_next_steps
    WHERE eventAction = 'interventionShown'
  ),

-- All distinct sessions that select the checker via the banner (eventCategory =
-- interventionBanner; eventAction = interventionClicked)

  sessions_next_steps_select AS (
    SELECT DISTINCT
      sessionId
    FROM sessions_next_steps
    WHERE eventAction = 'interventionClicked'
  ),

-- All distinct sessions that reject the checker via the banner (eventCategory =
-- interventionBanner; eventAction = interventionDismissed)

  sessions_next_steps_reject AS (
    SELECT DISTINCT
      sessionId
    FROM sessions_next_steps
    WHERE eventAction = 'interventionDismissed'
  ),

-- Join results

sessions_next_steps_all AS (
  SELECT
    COUNT(DISTINCT sessionId) AS sessionsThatShownBanner,
    (SELECT COUNT(DISTINCT sessionId) FROM sessions_next_steps_select) AS sessionsThatSelectBanner,
    (SELECT COUNT(DISTINCT sessionId) FROM sessions_next_steps_reject) AS sessionsThatRejectBanner,
  FROM sessions_next_steps_shown
)

-- The proportion of users that select the banner, reject the banner, and ignore
-- the banner

SELECT
  sessionsThatShownBanner,
  sessionsThatSelectBanner,
  CAST (100* (sessionsThatSelectBanner / sessionsThatShownBanner) AS NUMERIC) AS percentageSelectBanner,
  sessionsThatRejectBanner,
  CAST (100* (sessionsThatRejectBanner / sessionsThatShownBanner) AS NUMERIC) AS percentageRejectBanner,
  sessionsThatShownBanner -  (sessionsThatRejectBanner + sessionsThatSelectBanner) AS  sessionsThatIgnoreBanner,
  CAST (100* ((sessionsThatShownBanner -  (sessionsThatRejectBanner + sessionsThatSelectBanner)) / sessionsThatShownBanner) AS NUMERIC) AS percentageIgnoreBanner
FROM sessions_next_steps_all
