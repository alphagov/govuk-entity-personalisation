# Summary

The work in this folder gets standard English and govSpeak-specific synonyms for entities extracted from Named Entity Recognition in the Knowledge Graph. It uses several approaches to get these synonyms:
1. Calling an API linked to synonym.com to get standard English synonyms for single-term entities such as *'licence'*, *'sponsorship'* and *'department'*.
1. Generating word-embeddings to get govSpeak-specific synonyms using bag-of-words.
1. Generating word-embeddings to get govSpeak-specific synonyms using TF-IDF.
1. Generating word-embeddings to get govSpeak-specific single-term and double-term synonyms using Word2Vec (the Continuous Bag-of-Words version).

To take these word-embeddings and then get synonyms from them, we compute the cosine-similarity between the word-embedding vectors and then take those words with a cosine-similarity greater than 0.5 (the value space is [0, 1]).

## tl;dr
- Synonyms to entities can be used to improve Search.
- Generate these synonyms by running the following scripts:
    1. Download a copy of the pre-processed content store from S3 and put it in `data/raw/`.
    1. Run `notebooks/entities-synonyms/thesaurus.py`.
    1. Run `notebooks/entities-synonyms/00_preprocess_content_store.py`.
    1. Run `notebooks/entities-synonyms/01_cbow_embeddings.py`.
    1. Run `notebooks/entities-synonyms/02_cbow_embeddings.py`.
    1. Copy the files below into this [S3 bucket for the Knowledge Graph](https://s3.console.aws.amazon.com/s3/buckets/govuk-data-infrastructure-integration?region=eu-west-1&tab=objects).

## Word of warning
- When training the CBOW embeddings, one sacrifices reproducibility for speed. In particular, the script uses multiple cores to generate the embeddings (it took about an hour to train), but this means you cannot set the seed. Hence, do not expect to get the same word-embeddings when you run the scripts multiple times, though the cosine-similarity and henceforth the synonyms should not be too different. [[*Řehůřek, May 2020*](https://radimrehurek.com/gensim_3.8.3/models/word2vec.html)]

- The current code extends the identification of govSpeak-specific synonyms to single-and-double-term entities. Thus, we can get synonyms for *education* and *education provider* but we do not get synonyms for entities such as *department for education* nor *business, energy and industrial strategy*. To get these, one needs to extend the model in `01_cbow_embeddings.py`. A reference is provided in there on how to do it.

***

## What is it useful for?

The motivation is that once we have synonyms for each entity, we can better match entities with search queries.

> **Example:** *Consider that a user searches for 'school'. Then keyword matching search would return pages that contain content related to 'primary school', 'secondary school', 'applying to your local school' etc. However, the user may actually want results relating to universities (they just were not aware we call higher-education institutions universities in good ol' Blighty). Thus, using synonyms, we will be able to get the synonyms for 'school' to be 'higher education'. As 'higher education' exists as an entity to content with 'university' in it, then we can link the search result of 'school' with the content page of 'university' - all via the synonym linked to the entity of 'higher education'.*

Thus, we want to link the below query with synonyms and Search data:
```cypher
MATCH (c:Cid)-[r:HAS_ENTITY]-(e:Entity)
WHERE e.name CONTAINS "educat"
RETURN c, e, r
LIMIT 25;
```

## How about the other scripts?
There are other scripts in this folder, namely:
- `01_bow_tfidf_embeddings.py`
- `02_bow_tfidf_embeddings.py`

These scripts generate Bag-of-Word and TF-IDF word-embeddings which are then used to compute cosine-similarity with the entities to get these entities' synonyms. However, the results were really pants so we do not use these.
