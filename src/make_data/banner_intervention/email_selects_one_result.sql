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
      AND REGEXP_CONTAINS(hits.page.pagePath, r"^/run-business-from-home.*|^/renting-business-property-tenant-responsibilities.*|^/browse/business/premises-rates.*|^/running-a-limited-company/signs-stationery-and-promotional-material.*|^/business-finance-support?business_stages%5B%5D=not-yet-trading.*|^/business-coronavirus-support-finder.*|^/export-goods.*|^/research-export-markets.*|^/import-goods-into-uk.*|^/vat-registration.*|^/get-ready-to-employ-someone.*|^/browse/employing-people.*|^/corporation-tax.*|^/licence-finder.*|^https://www.abi.org.uk/products-and-issues/choosing-the-right-insurance/business-insurance/.*|^/check-if-you-need-tax-return.*|^/browse/business/sale-goods-services-data.*|^/cartels-price-fixing.*|^/data-protection-your-business.*|^https://www.hse.gov.uk/guidance/index.htm.*|^/browse/business/setting-up.*|^/running-a-limited-company/signs-stationery-and-promotional-material.*|^/managing-your-waste-an-overview.*|^/intellectual-property-an-overview.*|^/business-support-helpline.*|^/guidance/register-for-email-reminders-from-companies-house.*|^/vat-businesses.*")
      AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_email_select)
  )

-- The proportion of sessions that select the checker via the email that also
-- selects at least one results link on the results page

SELECT
  COUNT(DISTINCT sessionId) AS allSessionsThatSelectChecker,
  (SELECT COUNT(DISTINCT sessionId) FROM sessions_email_results) AS allSessionsThatAccessAtLeastOneResult,
  CAST (100 * (SELECT COUNT(DISTINCT sessionId) FROM sessions_email_results)/COUNT(DISTINCT sessionId) AS NUMERIC) AS proportionOfAllSessionsThatAccessAtLeastOneResult
FROM sessions_email_select
