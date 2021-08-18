## Summary of SQL scripts

#### Nonequivalent group (email)

- Users that register a limited company are sent an email by Companies House
  that provides them with a link to the Start a Business checker:
  `/next-steps-for-your-business`
- The nonequivalent group in this experiment is considered users who access SaB
  checker via email, as we know these users have just started a limited company.
- Proportions calculated in this user group are considered an *expected*
  proportion.

###### email_selects_results_page.sql ######
- This query extracts the proportion of users that access the results page (complete the checker) once
  selecting the SaB checker, i.e. total number of users that access the results
  page / total number of users that access the SaB checker via the email

###### email_selects_one_result.sql ######
- This query extracts the proportion of users that select at least one link on the
  results page once finishing the SaB checker, i.e. total number of users that
  select 1 link on the results page / total number of users that access the SaB
  checker the email

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

###### banner_selects_results_page.sql ######
- This query extracts the proportion of users that access the results page once
  selecting the SaB checker, i.e. total number of users that access the results
  page / total number of users that access the SaB checker via the banner

###### banner_selects_one_result.sql ######
- This query extracts the proportion of users that select at least one link on the
  results page once finishing the SaB checker, i.e. total number of users that
  select 1 link on the results page / total number of users that access the SaB
  checker via the banner

###### banner_select_reject_ignore.sql ######
- This query extracts the proportion of users that select the checker via the
  banner intervention, reject the checker via the banner intervention, and that
  ignore the checker via the banner intervention, i.e. total number of users that
  select the checker / total number of users that are shown the banner intervention;
  total number of users that reject the checker / total number of users that are
  shown the banner intervention; total number of users that ignore the checker /
  total number of users that are shown the banner intervention;

## Assumptions and caveats

#### Nonequivalent group (email)

- This group is defined by users that access the pagePath that starts with:
  `/next-steps-for-your-business?crn`. The query string `crn` represents users
  that have landed on the pagePath from the Companies House email.

###### email_selects_one_result.sql ######

- A REGEXP_CONTAINS statement defines all results pagePaths as a string that starts
  with the below, and matches any character, any number of times.
- These are the pagePaths included that are linked from the results page:
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

- A REGEXP_CONTAINS statement defines all results pagePaths as a string that starts
  with the below, and matches any character any number of times.
- The pagePaths that are linked from the results page are defined above under `email_selects_one_result.sql`

[SaBpages]: https://docs.google.com/spreadsheets/d/1CGogk1bgco1hYSSGsIcS-eZtdmWOhb-a6gIjkdMWFkQ/edit#gid=0
