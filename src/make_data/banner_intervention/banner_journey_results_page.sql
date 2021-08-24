/*
This query extracts the total number of journeys that visit the results page (i.e.
complete the checker) and the two SaB pagePaths that trigger the banner intervention.

- First, the query creates a table of all distinct sessions that select the banner
  and visits the results page of the checker (sessions_results_page).
- Next, the query only keeps SaB PAGE hits and the eventAction 'interventionClicked'
  from those sessions as defined above.
- Then, in hit order, the query calculates the previous pagePath of the EVENT action
  'interventionClicked' by counting 2 pagePaths back. NB: we look at 2 pagePaths
  back as 1 pagePath back is the same pagePath (the PAGE hit) as the EVENT hit
  'interactionClicked'
- Count the number of journeys for each pagePath and previousPagePath combination
  for 'interventionClicked' hits only (i.e. provide the pagePath combination that
  leads to the banner being selected).

No requirements to run this script. Uses `govuk-bigquery-analytics.87773428.ga_sessions_*`
output table.
*/


DECLARE start_date STRING DEFAULT "20210803";
DECLARE end_date STRING DEFAULT "20210816";

CREATE OR REPLACE TABLE `govuk-bigquery-analytics.banner_intervention.banner_journey_results_page` AS

-- All sessions that select the checker via the banner (eventAction =
-- interventionClicked)

WITH sessions_select_banner AS (
  SELECT
    CONCAT(fullVisitorId, "-", visitId) AS sessionId,
    hits.eventInfo.eventAction
  FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
  CROSS JOIN UNNEST(hits) AS hits
  WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
    AND hits.eventInfo.eventCategory = 'interventionBanner'
    AND hits.eventInfo.eventAction  = 'interventionClicked'
 ),

-- All sessions that select the banner and get to the end of the checker
-- (i.e. the results page)

sessions_results_page AS (
  SELECT
     CONCAT(fullVisitorId, "-", visitId) AS sessionId
  FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
  CROSS JOIN UNNEST(hits) AS hits
  WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
    AND STARTS_WITH(hits.page.pagePath, "/next-steps-for-your-business/results")
    AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_select_banner)
 ),

-- During those sessions which get to the end of the checker (i.e. the results page),
-- filter by SaB pages

sessions_journey AS (
  SELECT
    TIMESTAMP_MILLIS(CAST(hits.time + (visitStartTime * 1000) AS INT64)) AS datetime,
    CONCAT(fullVisitorId, "-", visitId) AS sessionId,
    hits.page.pagePath,
    hits.eventInfo.eventAction,
    hits.eventInfo.eventCategory,
    hits.type
  FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`
  CROSS JOIN UNNEST(hits) AS hits
  WHERE _TABLE_SUFFIX BETWEEN start_date AND end_date
    AND CONCAT(fullVisitorId, "-", visitId) IN (SELECT sessionId FROM sessions_results_page)
    AND REGEXP_CONTAINS(hits.page.pagePath, r"^/correct-your-business-rates$|^/send-rent-lease-details$|^/find-government-property$|^/contact-your-local-council-about-business-rates$|^/find-an-energy-assessor$|^/send-vat-return$|^/use-construction-industry-scheme-online$|^/file-your-company-accounts-and-tax-return$|^/pay-tax-direct-debit$|^/pay-tax-debit-credit-card$|^/marginal-relief-calculator$|^/barriers-trading-investing-abroad$|^/check-eori-number$|^/check-duties-customs-exporting$|^/get-rules-tariffs-trade-with-uk$|^/trade-tariff$|^/licence-finder$|^/file-your-confirmation-statement-with-companies-house$|^/file-changes-to-a-company-with-companies-house$|^/file-your-company-annual-accounts$|^/contracts-finder$|^/find-tender$|^/data-protection-register-notify-ico-personal-data$|^/check-when-businesses-pay-invoices$|^/digital-marketplace$|^/planning-permission-england-wales$|^/introduction-to-business-rates$|^/calculate-your-business-rates$|^/run-business-from-home$|^/apply-for-business-rate-relief$|^/energy-performance-certificate-commercial-property$|^/workplace-fire-safety-your-responsibilities$|^/workplace-temperatures$|^/renting-business-property-tenant-responsibilities$|^/scaffolding-rules$|^/terminating-a-commercial-property-lease-early$|^/can-i-use-cctv-at-my-commercial-premises$|^/water-and-sewerage-rates-for-businesses$|^/who-is-responsible-for-asbestos-found-in-my-commercial-property$|^/non-domestic-renewable-heat-incentive$|^/appeal-lawful-development-certificate-decision$|^/get-rebate-refund-business-rates$|^/get-your-air-conditioning-system-inspected$|^/register-boat-coastguard-safety-scheme$|^/right-to-contest-answer$|^/renewing-your-commercial-property-lease$|^/pay-vat$|^/pay-corporation-tax$|^/vat-registration$|^/vat-returns$|^/corporation-tax$|^/prepare-file-annual-accounts-for-limited-company$|^/capital-allowances$|^/company-tax-returns$|^/reclaim-vat$|^/tell-hmrc-changed-business-details$|^/corporation-tax-rates$|^/what-you-must-do-as-a-cis-subcontractor$|^/vat-businesses$|^/what-you-must-do-as-a-cis-contractor$|^/tax-buy-shares$|^/work-out-capital-allowances$|^/corporation-tax-accounting-period$|^/first-company-accounts-and-return$|^/vat-registration-thresholds$|^/capital-gains-tax-businesses$|^/dormant-company$|^/tax-compliance-checks$|^/tax-tribunal$|^/capital-allowances-sell-asset$|^/tax-when-your-company-sells-assets$|^/tax-limited-company-gives-to-charity$|^/pay-construction-industry-scheme-cis-late-filing-penalty$|^/get-refund-interest-corporation-tax$|^/government/collections/venture-capital-schemes-hmrc-manuals$|^/wood-packaging-import-export$|^/take-goods-sell-abroad$|^/taking-goods-out-uk-temporarily$|^/intrastat$|^/research-export-markets$|^/overseas-customers-export-opportunities$|^/eori|$^/goods-sent-from-abroad$|^/vat-on-services-from-abroad$|^/limited-company-formation$|^/strike-off-your-company-from-companies-register$|^/running-a-limited-company$|^/closing-a-limited-company$|^/directors-loans$|^/annual-accounts$|^/search-the-register-of-disqualified-company-directors$|^/audit-exemptions-for-private-limited-companies$|^/change-your-companys-year-end$|^/register-as-an-overseas-company$|^/company-director-disqualification$|^/appeal-a-penalty-for-filing-your-company-accounts-late$|^/make-changes-to-your-limited-company$|^/queens-awards-for-enterprise$|^/object-to-a-limited-company-being-struck-off$|^/set-up-property-management-company$|^/restart-a-non-trading-or-dormant-company$|^/cartels-price-fixing$|^/file-accounts-in-the-uk-as-an-overseas-company$|^/accepting-returns-and-giving-refunds$|^/online-and-distance-selling-for-businesses$|^/trading-hours-for-retailers-the-law$|^/invoicing-and-taking-payment-from-customers$|^/data-protection-your-business$|^/tendering-for-public-sector-contracts$|^/product-labelling-the-law$|^/weights-measures-and-packaging-the-law$|^/marketing-advertising-law$|^/pedlars-certificate$|^/doorstep-selling-regulations$|^/respond-data-protection-request$|^/unfair-terms-in-sales-contracts$|^/entertainment-and-modelling-agencies$|^/uk-registered-deaths$|^/employers-liability-insurance$|^/employment-agencies-and-businesses$|^/growing-your-business$|^/employing-staff$|^/set-up-business$")
),

-- Only keep PAGE hits and the eventAction 'interventionClicked'. Calculate the
-- previous pagePath. Do this by counting 2 pagePaths back. This is because for
-- 'interventionClicked' hit, the pagePath is the same as one pagePath back (as 1
-- pagePath back is the PAGE hit). 2 pagePaths back is the PAGE hit before the
-- banner is shown.

previous_pages AS (
    SELECT
        datetime,
        sessionId,
        pagePath,
        LAG(pagePath,2)OVER(PARTITION BY sessionId ORDER BY datetime) AS previousPagePath,
        eventAction
    FROM sessions_journey
    WHERE (type = 'PAGE' OR eventAction = 'interventionClicked')
    ORDER BY datetime
),

-- Only keep sessions when the user selected the banner (eventAction =
-- 'interventionClicked')

journeys_clicked AS (
    SELECT DISTINCT
        sessionId,
        pagePath,
        previousPagePath
    FROM previous_pages
    WHERE eventAction = 'interventionClicked'
)

-- Count the number of journeys for each pagePath and previousPagePath combination

SELECT
    pagePath,
    previousPagePath,
    COUNT(*) as n
FROM journeys_clicked
GROUP BY pagePath, previousPagePath
ORDER BY n DESC
