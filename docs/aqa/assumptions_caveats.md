# Assumptions and caveats Log

This log contains a list of assumptions and caveats used in this analysis.

<!-- Use reStructuredText contents directive to generate a local contents -->
```eval_rst
.. contents::
    :local:
    :depth: 1
```

## Definitions

Assumptions are RAG-rated according to the following definitions for quality and impact<sup>1</sup>:

<!-- Using reStructuredText table here, otherwise the raw Markdown is greater than the 120-character line width -->
```eval_rst
+-------+------------------------------------------------------+-------------------------------------------------------+
| RAG   | Assumption quality                                   | Assumption impact                                     |
+=======+======================================================+=======================================================+
| GREEN | Reliable assumption, well understood and/or          | Marginal assumptions; their changes have no or        |
|       | documented; anything up to a validated & recent set  | limited impact on the outputs.                        |
|       | of actual data.                                      |                                                       |
+-------+------------------------------------------------------+-------------------------------------------------------+
| AMBER | Some evidence to support the assumption; may vary    | Assumptions with a relevant, even if not critical,    |
|       | from a source with poor methodology to a good source | impact on the outputs.                                |
|       | that is a few years old.                             |                                                       |
+-------+------------------------------------------------------+-------------------------------------------------------+
| RED   | Little evidence to support the assumption; may vary  | Core assumptions of the analysis; the output would be |
|       | from an opinion to a limited data source with poor   | drastically affected by their change.                 |
|       | methodology.                                         |                                                       |
+-------+------------------------------------------------------+-------------------------------------------------------+
```
<sup><sup>1</sup> With thanks to the Home Office Analytical Quality Assurance team for these definitions.</sup>

## Assumptions and caveats

The log contains the following assumptions and caveats:

<!-- Use reStructuredText contents directive to generate a local contents -->
```eval_rst
.. contents::
    :local:
    :depth: 1
```

### Assumption 1: Search terms can be extracted from `pagePath`

* **Quality**: Green
* **Impact**: Red

Found that there are two competing methods for extracting search terms on GOV.UK Search. They are:
1. [Search Analysis](https://github.com/alphagov/govuk-entity-personalisation/blob/main/src/make_data/longterm_searchquerysample.sql)
1. [User-journeys Analysis](https://github.com/alphagov/govuk-user-journey-models/blob/master/queries/joining_user-intent-data_big-query.sql)

The former looks at Search terms only whereas latter looks at user-journeys, some of which can contain search terms.

This assumption applies to `src/make_data/search_uis.sql` where we want the journey data for people who make searches.
This is so we can assess whether the search results gives them their intended results. It will allow us to thus
benchmark robustly our Search approaches to see which one performs better.

From eyeballing the below query, we find that the two methods for extracting search terms are equivalent.

```sql
SELECT DISTINCT
  hits.page.pagePath,
  hits.page.searchKeyword
FROM `govuk-bigquery-analytics.87773428.ga_sessions_*`,
  UNNEST(hits) AS hits
WHERE
  hits.page.searchKeyword IS NOT NULL
  AND _table_suffix BETWEEN FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY))
  AND FORMAT_DATE('%Y%m%d',DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY));
```

### Assumption 2: Insert plain English title here

* **Quality**: Insert RAG rating here
* **Impact**: Insert RAG rating here

Add plain English description here.
