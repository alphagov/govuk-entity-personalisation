/*
This scripts provides the number and proportion of sessions where the user has left
feedback about the quality of the page where the banner is shown ("feedback sessions").

- The user replied to the feedback request at the bottom of a page: "Is this
  page useful? Yes/No"
- "Feedback sessions" must contain one of the following events:
  eventAction == "ffNoClick" OR ffYesClick"
- The feedback (recorded as an EVENT hit) is assigned to the corresponding
  pagePath associated with the EVENT hit
- "Feedback sessions" are sessions that are shown the banner, and immediately provides
  feedback (nextEventAction) on the same pagePath they are shown the banner (nextPagePath).

No requirements to run this script. Uses `govuk-bigquery-analytics.87773428.ga_sessions_*`
output table.
*/


DECLARE start_date STRING DEFAULT "20210803";
DECLARE end_date STRING DEFAULT "20210816";

CREATE OR REPLACE TABLE `govuk-bigquery-analytics.banner_intervention.banner_feedback` AS

-- All sessions that are shown the checker via the banner (eventAction =
-- interventionShown)

WITH
  sessions_banner AS (
    SELECT
        CONCAT(fullVisitorId, "-", visitId) AS sessionId
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
    WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
      AND hits.eventInfo.eventCategory = 'interventionBanner'
      AND hits.eventInfo.eventAction = 'interventionShown'
  ),

-- All sessions that leave feedback (eventAction = "ffNoClick" OR
-- eventAction = "ffYesClick")

sessions_feedback AS (
    SELECT
      CONCAT(fullVisitorId, "-", visitId) AS sessionId,
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
        WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
        AND (hits.eventInfo.eventAction = "ffNoClick"
        OR hits.eventInfo.eventAction = "ffYesClick")
),

-- All sessions that leave feedback and are shown the banner during the same session.
-- Keep all EVENT hits and the eventCategory and eventAction.

sessions_shown_banner_feedback AS (
    SELECT
        TIMESTAMP_MILLIS(CAST(hits.time + (visitStartTime * 1000) AS INT64)) AS datetime,
        CONCAT(fullVisitorId, "-", visitId) AS sessionId,
        hits.page.pagePath,
        hits.eventInfo.eventCategory,
        hits.eventInfo.eventAction
    FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
    CROSS JOIN UNNEST(hits) AS hits
    WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
        AND hits.type = 'EVENT'
        AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_feedback)
        AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_banner)
),

-- For each session, order by datetime. Flag the following eventAction (nextEventAction)
-- and the following pagePath (nextPagePath) for each hit.

sessions_next_event_next_path AS (
    SELECT
        *,
         LEAD(eventAction,1)OVER(PARTITION BY sessionId ORDER BY datetime) AS nextEventAction,
         LEAD(pagePath,1)OVER(PARTITION BY sessionId ORDER BY datetime) AS nextPagePath
    FROM sessions_shown_banner_feedback
),

-- Only keep sessions that are shown the banner, provide feedback, and do this on
-- the same pagePath they are shown the banner (nextPagePath). This table provides
-- a summary of the sessions that leave feedback on the same page that the banner
-- is shown (once the banner is shown).

sessions_banner_feedback AS (
    SELECT
        *
    FROM sessions_next_event_next_path
    WHERE eventAction = 'interventionShown'
        AND (nextEventAction = "ffNoClick" OR nextEventAction = "ffYesClick")
        AND pagePath = nextPagePath
),

-- Count sessionIds for each feedback type (nextEventAction)

sessions_feedback_count AS (
    SELECT
        nextEventAction,
        COUNT(DISTINCT sessionId) AS totalNumberOfSessions
    FROM sessions_banner_feedback
    GROUP BY nextEventAction
)

-- Calculate proportion

SELECT
    nextEventAction,
    totalNumberOfSessions,
    (SELECT COUNT(DISTINCT sessionId) FROM sessions_banner) as totalNumberOfSessionsThatShownBanner,
    CAST (100 *  totalNumberOfSessions /  (SELECT COUNT(DISTINCT sessionId) FROM sessions_banner) AS NUMERIC) AS proportionOfSessionsThatLeaveFeedback
FROM sessions_feedback_count
group by nextEventAction, totalNumberOfSessions
