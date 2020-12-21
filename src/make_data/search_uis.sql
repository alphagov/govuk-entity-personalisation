/* GA Sessions x UIS */
-- Query to join user-intents-survey data to sessions data on BigQuery
-- Reference:
--  https://github.com/alphagov/govuk-user-journey-models/blob/master/queries/joining_user-intent-data_big-query.sql#L150
--
-- ## Notes
-- The `clientID` field is the only field that is in common between BigQuery and the uis-data.
-- Upload uis-data to BQ using the following schema in the "Edit as text" format:
-- Started:STRING,Ended:STRING,Tracking_Link:STRING,Page_Path:STRING,clientID:STRING,Q1:STRING,Q4:STRING,Q5:STRING,target:STRING,respondent_id:INTEGER,full_url:STRING,page:STRING,section:STRING,org:STRING,Started_Date:STRING,Ended_Date:STRING,Started_Date_sub_12h:STRING

-- `clientID` is a floating point value up to 10 decimal places. BigQuery stores this value as a string. Worth noting that BigQuery has a technical limit where it can only process numbers that have decimal places up to 9 positions. Depending on how you've configured the table, a number of strategies could be employed:
--     + Multiply `clientID` by a multiple of 10, to reduce the number of decimal places.
--     + Cast as FLOAT64.
--     + Encode `clientID` as STRING. `clientID` is encoded as STRING in BQ.
--
-- `clientID` can be attached to multiple sessions, and each session can contain multiple events.
-- To support with finding the correct corresponding session on ga, we are filtering `eventCategory`, and `eventAction` for events related to completing a survey response.

-----
-- unnest hits to get info from each pageview
-- extract custom dimensions
WITH ga_select_cols AS (
  SELECT
    clientId,
    CONCAT(fullVisitorId, '-', clientId, '-', CAST(visitId AS STRING), '-', CAST(visitNumber AS STRING)) AS session_id,
    date,
    fullVisitorId,
    visitId,
    visitNumber,
    visitStartTime,
    channelGrouping,
    totals.timeOnSite AS total_seconds_in_session,
    totals.pageviews AS pageviews,
    hits.hitNumber as hitNumber,
    hits.eventInfo.eventCategory AS eventCategory,
    hits.eventInfo.eventAction AS eventAction,
    hits.page.pagePath AS hits_pagePath,
    hits.type AS hit_type,
    -- get document type of each page
    (SELECT value FROM hits.customDimensions WHERE index=2) AS page_format,
    -- get the first digit of status codes, so we can count how many 4xx and 5xx errors each session has
    SUBSTR(SAFE_CAST(
      (SELECT
        value
      FROM
        hits.customDimensions
      WHERE
        index=15) AS STRING),0, 1) AS statusCodeType,
    -- get top level taxons for each page
    (SELECT value FROM hits.customDimensions WHERE index=3) AS top_level_taxons,
  FROM
    `govuk-bigquery-analytics.87773428.ga_sessions_*` AS sessions
  CROSS JOIN
    UNNEST(sessions.hits) AS hits
  -- filter to just the days you want to look at/join survey data to
  WHERE
    _TABLE_SUFFIX BETWEEN '20200311' AND '20200312'
),

-- aggregate on a session_id and date level
ga_aggregated AS (
  SELECT
    clientId,
    session_id,
    -- need to dedupe sessions at the end so we don't join a survey to two days of the same session
    date,
    fullVisitorId,
    visitId,
    visitNumber,
    -- MIN/MAX here to get one row per session ID, just in case these columns are occasionally null/differ
    MIN(visitStartTime) as min_visitStartTime,
    MAX(channelGrouping) AS channelGrouping,
    MAX(total_seconds_in_session) AS total_seconds_in_session,
    MAX(pageviews) AS pageviews_in_session,

    -- flag for if a done page was seen in that session
    MAX(CASE WHEN hit_type = 'PAGE' AND page_format = 'completed_transaction' THEN 1 ELSE 0 END) AS done_page_flag,
    -- get sequences of pages viewed, events, events with pages, top level taxons, and page formats viewed
    STRING_AGG(CONCAT(eventCategory, ' <:< ', eventAction), ' >> ' ORDER BY hitNumber) AS events_sequence,
    STRING_AGG(
      CONCAT(hits_pagePath,' << ',
        CONCAT(hit_type, ' <:< ', IFNULL(eventCategory,"NULL"), ' <:< ', IFNULL(eventAction,"NULL"))
      ), ' >> ' ORDER BY hitNumber) AS Sequence,
    STRING_AGG(
      IF(hit_type = 'PAGE', hits_pagePath,  NULL),
      ' >> ' ORDER BY hitNumber) AS PageSequence,
    STRING_AGG(
      IF(hit_type = 'PAGE' AND REGEXP_CONTAINS(hits_pagePath, r"/search/"), REGEXP_EXTRACT(hits_pagePath, r"keywords=(.+)"), NULL),
      ' >> ' ORDER BY hitNumber) AS search_terms_sequence,
    STRING_AGG(
      IF(hit_type = 'PAGE' AND REGEXP_CONTAINS(hits_pagePath, r"/search/"), REPLACE(REGEXP_EXTRACT(hits_pagePath, r"keywords=(.+?)&"),'+', ' '), NULL),
      ' >> ' ORDER BY hitNumber) AS cleaned_search_terms_sequence,
    -- potential indicators that this was the session that the survey started at
    MAX(
      CASE WHEN
        eventCategory = 'External Link Clicked' AND REGEXP_CONTAINS(eventAction,'.*smartsurvey.*') OR
        eventCategory = 'Onsite Feedback' AND eventAction IN ('GOV.UK Close Form', 'GOV.UK Open Form', 'GOV.UK Send Form') OR
        eventCategory = 'yesNoFeedbackForm' AND eventAction IN ('ffNoClick', 'Send Form') OR
        eventCategory = 'user_satisfaction_survey' AND eventAction IN ('banner_shown', 'banner_taken')
      THEN 1 ELSE 0 END)  AS flag_for_criteria
  FROM ga_select_cols
  GROUP BY
    clientId,
    session_id,
    date,
    fullVisitorId,
    visitId,
    visitNumber
),

-- when a session spans more than one day, aggregate over the whole session
ga AS (
  SELECT
    clientId,
    session_id,
    date,
    fullVisitorId,
    visitId,
    visitNumber,
    MIN(min_visitStartTime) OVER (PARTITION BY session_id) AS min_visitStartTime_across_days,
    -- extract a timestamp from the POSIX timestamp, get the minimum start datetime across all days the session happened over
    TIMESTAMP_SECONDS(MIN(min_visitStartTime) OVER (PARTITION BY session_id)) AS min_visitStartTimestamp_across_days,
    -- leaving in raw country data without grouping in case we want to change our groupings in Python before finalising this query

    channelGrouping,

    MAX(done_page_flag) OVER (PARTITION BY session_id) AS done_page_flag,

    SUM(total_seconds_in_session) OVER (PARTITION BY session_id) AS total_seconds_in_session_across_days,
    SUM(pageviews_in_session) OVER (PARTITION BY session_id) AS total_pageviews_in_session_across_days,

    STRING_AGG(events_sequence, ' >> ')
      OVER (PARTITION BY session_id ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS events_sequence,
    STRING_AGG(Sequence, ' >> ')
      OVER (PARTITION BY session_id ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS Sequence,
    STRING_AGG(PageSequence, ' >> ')
      OVER (PARTITION BY session_id ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)  PageSequence,
    STRING_AGG(search_terms_sequence, ' >> ')
      OVER (PARTITION BY session_id ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS search_terms_sequence,
    STRING_AGG(cleaned_search_terms_sequence, ' >> ')
      OVER (PARTITION BY session_id ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS cleaned_search_terms_sequence,
    MAX(flag_for_criteria) OVER (PARTITION BY session_id) AS flag_for_criteria
  FROM
    ga_aggregated
  )

-- join GA data to user intents survey, get unique session_id:survey response pairs
SELECT DISTINCT
    intents.primary_key,
    intents.clientID AS intents_clientID,
    ga.fullVisitorId,
    ga.visitId,
    ga.visitNumber AS ga_visitNum,
    intents.Started,
    intents.Ended,
    -- Have you found what you were looking for?
    intents.Q4,
    -- Overall, how did you feel about your visit to GOV.UK today?
    intents.Q5,
    -- Have you been anywhere else for help with this already?
    intents.Q6,
    ga.session_id,
    ga.date AS ga_date,

    ga.total_seconds_in_session_across_days,
    ga.total_pageviews_in_session_across_days,
    -- when the session started and ended
    ga.min_visitStartTimestamp_across_days AS ga_visit_start_timestamp,
    TIMESTAMP_SECONDS(ga.min_visitStartTime_across_days + ga.total_seconds_in_session_across_days) AS ga_visit_end_timestamp,
    intents.Started_Date AS intents_started_date,
    -- pages/events/search terms - for use in user intents survey app for people to explore journeys and feedback
    ga.events_sequence,
    ga.search_terms_sequence,
    -- can used this to count unique search terms in Python
    ga.cleaned_search_terms_sequence,
    ga.Sequence,
    ga.PageSequence,

    ga.flag_for_criteria,
    -- flag for if the url the survey was initiated on was present in that session
    CASE
        WHEN intents.page_path IN UNNEST(SPLIT(ga.PageSequence, '>>')) THEN 1
        ELSE 0
        END AS full_url_in_session_flag
FROM
    `govuk-bigquery-analytics.datascience.user_intent_survey_20191023_20200311` AS intents
INNER JOIN ga
    -- uploaded `clientID` as a string, and `clientID` is stored as a string in BQ.
  ON intents.clientID = ga.clientId
  -- check that the session started on the same day as the survey,
  -- or the day 12 hours before the survey was started
  -- (i.e. if the survey was started as 1am the session may have started before midnight the previous day)
  AND ga.date BETWEEN intents.Started_Date_sub_12h AND intents.Started_Date
  AND PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', intents.Started) > ga.min_visitStartTimestamp_across_days
WHERE intents.Started_Date > '20191231'
-- Previously we filtered `ga.eventCategory` and `ga_eventAction` for relevant events to survey response.
-- We could also filter on the page that triggered the survey (in the survey data) being in the session
-- for now as we don't know if the user is providing feedback on a specific session or all their browsing that day we won't narrow it down as much
-- WHERE
  -- ga.flag_for_criteria = 1
-- this ordering helps keep the output readable, as all sessions with the same client ID are together
ORDER BY
    intents.clientID,
    ga.visitNumber ASC;
