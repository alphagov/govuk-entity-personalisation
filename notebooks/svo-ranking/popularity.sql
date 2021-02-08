SELECT
    date
    ,hits.page.pagePath
    ,COUNT(hits.page)
FROM
    `govuk-bigquery-analytics.87773428.ga_sessions_intraday_*`,
    UNNEST(hits) AS hits
WHERE
    _table_suffix > FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
        AND hits.type = "PAGE"
GROUP BY
    date
    ,hits.page.pagePath;
