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
  immediately following the EVENT hit `interactionShown`, even if the pagePath of
  the EVENT hit `interactionShown` is the same as EVENT hit `ffNoClick` or `ffYesClick`.

[SaBpages]: https://docs.google.com/spreadsheets/d/1CGogk1bgco1hYSSGsIcS-eZtdmWOhb-a6gIjkdMWFkQ/edit#gid=0
