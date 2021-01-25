# How does this work?
Idea is to extract the intent part of a free text field. What I do is I manually label the data with what I think is the intent string from the free text field.

> e.g. I have two partners, six kids, and juggle three jobs. I want to find out about benefits I am eligible for so I can look after my six kids without the pressure of juggling three jobs -> I want to find out about benefits

Then I apply Parts-of-Speech tagging to identify things like verbs, nouns, pronouns etc. on the free text field.
> e.g. I want to find out about benefits -> `PRON`, `VERB`, `PART`, `VERB`, `ADP`, `ADP`, `NOUN`

Once I have done that, I want to see the most frequent Parts-of-Speech that exist in the manually-extracted intent string.
> e.g. `PRON`, `VERB`, `PART`, `ADP`, `NOUN`

I then use the most frequent Parts-of-Speech tags to filter my original free text field. This is in the hope that after filtering, I get the intent only.
> e.g. Filtering for `PRON`, `VERB`, `PART`, `ADP`, `NOUN` -> I want to find out about benefits…
