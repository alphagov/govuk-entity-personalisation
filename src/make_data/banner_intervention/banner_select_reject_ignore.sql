/* This query extracts the total number and proportion of sessions that select the
   checker via the banner intervention, reject the checker via the banner
   intervention, and that ignore the checker via the banner intervention.
*/


DECLARE start_date STRING DEFAULT "20210803";
DECLARE end_date STRING DEFAULT "20210816";

CREATE OR REPLACE TABLE `govuk-bigquery-analytics.banner_intervention.banner_select_reject_ignore` AS

-- All sessions that are shown the checker via the banner (eventCategory =
-- interventionBanner) and are shown the banner (interventionShown), select the
-- banner (interventionClicked), and dismiss the banner (interventionDismissed)

WITH sessions_flags AS (
     SELECT
          CONCAT(fullVisitorId, "-", visitId) AS sessionId,
          MAX(CASE WHEN hits.eventInfo.eventAction = 'interventionShown' THEN 1 ELSE 0 END) AS banner_shown,
          MAX(CASE WHEN hits.eventInfo.eventAction = 'interventionClicked' THEN 1 ELSE 0 END) AS banner_clicked,
          MAX(CASE WHEN hits.eventInfo.eventAction = 'interventionDismissed' THEN 1 ELSE 0 END) AS banner_rejected
      FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
      CROSS JOIN UNNEST(hits) AS hits
      WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
        AND hits.eventInfo.eventCategory = 'interventionBanner'
      GROUP BY CONCAT(fullVisitorId, "-", visitId)
),

sessions_next_steps_all AS (
  SELECT
    SUM(banner_shown) AS sessionsThatShownBanner,
    SUM(banner_clicked) AS sessionsThatSelectBanner,
    SUM(banner_rejected) AS sessionsThatRejectBanner,
  FROM sessions_flags
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
