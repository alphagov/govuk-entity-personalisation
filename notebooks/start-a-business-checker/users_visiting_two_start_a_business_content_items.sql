WITH target_pages_sessions AS (
    SELECT 
        CONCAT(fullVisitorId, "-", CAST(visitId AS STRING)) AS sessionId,
        hits.page.pagePath,
    	FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`, UNNEST(hits) AS hits
        WHERE hits.type = 'PAGE' AND hits.page.pagePath in UNNEST(@pages) AND _TABLE_SUFFIX BETWEEN @date_from AND @date_to
            
),

count_distinct_pages_per_session AS (
    SELECT 
        sessionid, 
        COUNT(distinct pagepath) as countOfDistinctPages
        FROM target_pages_sessions
    GROUP BY sessionId

)

SELECT 
    COUNT(Sessionid) AS numberOfSessions, 
    countOfDistinctPages
FROM count_distinct_pages_per_session
GROUP BY countOfDistinctPages
ORDER BY countOfDistinctPages
