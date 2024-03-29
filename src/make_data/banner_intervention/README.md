## Summary of SQL scripts

#### Nonequivalent group (email)

- Users that register a limited company are sent an email by Companies House
  that provides them with a link to the Start a Business checker:
  `/next-steps-for-your-business`
- The nonequivalent group in this experiment is considered users who access SaB
  checker via email, as we know these users have just started a limited company.

###### email_feedback_results_page.sql

- This script provides the number and proportion of sessions where the user has
  left feedback about the quality of the results page of the checker, only if they
  have accessed the checker via the Companies House email i.e. total number of
  sessions that leave feedback on the results page / total number of sessions that
  access the results page
- Proportions calculated in this user group are considered an *expected*
  proportion.

###### email_selects_results_page.sql ######
- This query extracts the proportion of sessions that access the results page (complete
  the checker) once selecting the SaB checker, i.e. total number of sessions that access
  the results page / total number of sessions that access the SaB checker via the email

###### email_selects_one_result.sql ######
- This query extracts the proportion of sessions that select at least one link on the
  results page once finishing the SaB checker, i.e. total number of sessions that
  select 1 link on the results page / total number of sessions that access the SaB
  checker via the email

#### Experimental group (banner intervention)

- gov.uk users that access at least two Start a Business pages (as defined in this
 [Google Sheet document][SaBpages]) are presented with a banner that suggests that they might
 want to visit the Start a Business checker.
- The banner is tracked on Google Analytics as an EVENT hit:
  - When users are shown the banner: `eventCategory = 'interventionBanner'`
                                     `eventAction = 'interventionShown'`
  - When users select the banner:    `eventCategory = 'interventionBanner'`
                                     `eventAction = 'interventionClicked'`
  - When users reject the banner:    `eventCategory = 'interventionBanner'`
                                     `eventAction = 'interventionDismissed'`

###### banner_feedback_results_page.sql

- This script provides the number and proportion of sessions where the user has
  left feedback about the quality of the results page of the checker, only if they
  have accessed the checker via the banner intervention i.e. total number of
  sessions that leave feedback on the results page / total number of sessions that
  access the results page

###### banner_feedback.sql

- This scripts provides the number and proportion of sessions where the user has
  left feedback about the quality of the page where the banner is shown i.e. total
  number of sessions that leave feedback on the banner trigger page / total number
  of sessions that are shown the banner.

###### banner_journey_results_page.sql

- This query extracts the total number of journeys that visit the results page (i.e.
  completes the checker), and groups by the two SaB pagePaths that trigger the banner
  intervention.
- This will provide us with an understanding of which pagePaths are most most likely
  to result in user engagement with the checker.

###### banner_journey_results_link.sql

- This query extracts the total number of journeys that select at least 1 link on
  the results page, and groups by the two SaB pagePaths that trigger the banner
  intervention.
- This will provide us with an understanding of which pagePaths are most most likely
  to result in user engagement with the checker.
=======
###### banner_selects_results_page.sql ######
- This query extracts the proportion of sessions that access the results (complete
  the checker) page once selecting the SaB checker, i.e. total number of sessions
  that access the results page / total number of sessions that access the SaB checker
  via the banner

###### banner_selects_one_result.sql ######
- This query extracts the proportion of sessions that select at least one link on
  the results page once finishing the SaB checker, i.e. total number of sessions
  that select 1 link on the results page / total number of sessions that access the
  SaB checker via the banner

###### banner_select_reject_ignore.sql ######
- This query extracts the proportion of sessions that select the checker via the
  banner intervention, reject the checker via the banner intervention, and that
  ignore the checker via the banner intervention, i.e. total number of sessions that
  select the checker / total number of sessions that are shown the banner intervention;
  total number of sessions that reject the checker / total number of sessions that
  are shown the banner intervention; total number of sessions that ignore the checker
  / total number of sessions that are shown the banner intervention;

## Assumptions and caveats

#### Nonequivalent group (email)

- This group is defined by users that access the pagePath that starts with:
`/next-steps-for-your-business?crn`. The query string `crn` represents users
that have landed on the pagePath from the Companies House email.

#### Experimental group (banner intervention)

###### banner_feedback.sql

- This script aims to identify sessions that leave feedback on the page the banner
  intervention is shown.
- This script calculates feedback sessions of interest as sessions that have an
  EVENT hit `ffNoClick` or `ffYesClick` (i.e. provide feedback) immediately following
  an EVENT hit `interactionShown` (i.e. shown the banner).
- In addition, these two EVENT hits must have the same pagePath.
- Therefore, it does not include sessions where other PAGE or EVENT hits occur
  immediately following the EVENT hit `interactionShown`, and the EVENT hit
  `ffNoClick` or `ffYesClick`. It sill does not include other PAGE or EVENT hits
  even if the pagePath of the EVENT hit `interactionShown` is the same as EVENT
  hit `ffNoClick` or `ffYesClick`.

###### banner_journey_results_page.sql

- This script aims to determine the two SaB pagePaths that result in the banner
  being triggered.
- It does this by only keeping SaB PAGE hits and the eventAction 'interventionClicked'.
  - It then counts 2 pagePaths back and flags the pagePath.
  - This is because for an 'interventionClicked' EVENT hit, the pagePath is the
    same as one pagePath back (as 1 pagePath back is the PAGE hit). 2 pagePaths
    back is the PAGE hit before the banner is shown.
- It therefore makes the assumption that the two SaB pagePaths result in the banner
  being triggered.
- There are instances where the previousPagePath (2 pagePaths back) is `NULL`.
  This could happen when a user session ends, because, for example, there is a 30
  minute period of inactivity, or they have visited a DONE page from a cross-domain
  page. Therefore, the user visited 1 SaB page in session 1, and a second SaB page
  in session 2, then shown the banner in session 2. As this query analyses at the
  session level, it is not able to extract the previousPagePath which is visited
  in session 1.
- There are instances where the previousPagePath and the pagePath are the same SaB
  page. This could happen when a user refreshes a SaB page, and so this is recorded
  as 2 PAGE hits (which triggers the banner). It could also be because although
  there are multiple PAGE hits during a session, the user only visited 1 SaB page.
  Then, the user visited the same SaB page at another time during the session,
  which triggered the banner being shown.

###### banner_journey_results_link.sql
- Subject to the same caveats and assumptions as `banner_journey_results_page.sql`

###### email_selects_one_result.sql ######

- When a user selects a link on the results page, this is tracked as an EVENT hit:
  `eventCategory = 'SmartAnswerClicked', eventLabel = 'the url they select'`
- Therefore, by filtering sessionIds by `eventCategory = 'SmartAnswerClicked` will
  filter all sessionIds that click at least 1 link on the results page.
- In the future, the 'SmartAnswerClicked' eventCategory may be used for other types
  of interactions. Therefore, future analyses also may need to filter by eventLabel.
  However, for the current analyses, run between 03082021 - 16082021, this is not the
  case.
- These are the pagePaths that can be present in the eventLabel (i.e. the pages that
  are linked from the results page):
`/run-business-from-home`
`/renting-business-property-tenant-responsibilities`
`/browse/business/premises-rates`
`/running-a-limited-company/signs-stationery-and-promotional-material`
`/business-finance-support?business_stages%5B%5D=not-yet-trading`
`/business-coronavirus-support-finder`
`/export-goods`
`/research-export-markets`
`/import-goods-into-uk`
`/vat-registration`
`/vat-registration/when-to-register`
`/get-ready-to-employ-someone`
`/browse/employing-people`
`/corporation-tax`
`/licence-finder`
`https://www.abi.org.uk/products-and-issues/choosing-the-right-insurance/business-insurance`
`/check-if-you-need-tax-return`
`/browse/business/sale-goods-services-data`
`/cartels-price-fixing`
`/data-protection-your-business`
`https://www.hse.gov.uk/guidance/index.htm`
`/browse/business/setting-up`
`/running-a-limited-company/signs-stationery-and-promotional-material`
`/managing-your-waste-an-overview`
`/intellectual-property-an-overview`
`/business-support-helpline`
`/guidance/register-for-email-reminders-from-companies-house`
`/vat-businesses`


#### Experimental group (banner intervention)

###### banner_select_reject_ignore.sql ######

- If an end-user visits a page where the banner is shown, and then either clicks
  a response to the banner in a new tab, or has a period of 30 minutes of inactivity
  on gov.uk before responding to the banner, then, for example, `interventionShown`
  and `interventionClicked` EVENT hits are recorded during different sessions.
  <br>
  - As such, when calculating when the banner is ignored (as there is not a specific
    EVENT hit), keeping sessions where `interventionShown`, which do not also have
    an `interventionClicked` or `interventionDimissed` EVENT, will provide
    incorrect results. For example: <br>
    `SELECT DISTINCT sessionId`
    `FROM sessions_next_steps_shown t1`
    `WHERE NOT EXISTS (SELECT sessionId FROM sessions_next_steps_select t2 WHERE`
     `t1.sessionId = t2.sessionId)`
      `AND NOT EXISTS (SELECT sessionId FROM sessions_next_steps_reject t3 WHERE`
      `t1.sessionId = t3.sessionId)`<br>
    This query will not include a sessionId if the sessionId only has an 'interventionClicked'
    or 'interventionDismissed' hit, and does not include an 'interventionShown' hit.
    Therefore, there is a discrepancy in the count data as sessionIds that have been
    included in the sessions_next_steps_select and sessions_next_steps_reject tables
    have been incorrectly not included in this calculation.
    <br>
  - Therefore the number of sessions that ignore the banner has been calculated by
    subtracting the number of sessions the either select or dismiss the banner,
    from the number of sessions that are shown the banner.

###### banner_selects_one_result.sql ######

- Subject to the same caveats and assumptions as `email_selects_one_result.sql`

[SaBpages]: https://docs.google.com/spreadsheets/d/1CGogk1bgco1hYSSGsIcS-eZtdmWOhb-a6gIjkdMWFkQ/edit#gid=0
