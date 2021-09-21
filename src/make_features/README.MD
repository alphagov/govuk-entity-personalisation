# Subject Verb Object Autocomplete

These scripts are part of the process of extracting subject verb object relationships between words in content item titles.
They should be run in the order given here.
Some of the steps output intermediate files, there is no need to copy these to `search-autocomplete-api` - only the files listed below need to be copied.

### Prerequisites

* Virtualenv running Python 3.7 (why 3.7? The version of Gensim we're using is not tested beyond it)
* Access to Google BigQuery (see [here](https://docs.publishing.service.gov.uk/manual/datalabs-bigquery.html#get-access-to-google-bigquery) for details on how to get it). You'll want to have a credentials file and the correct [environment variable](https://cloud.google.com/docs/authentication/getting-started#setting_the_environment_variable) set up.


### Part 1. Generating new SVO data for SVO Autocomplete

1. Download the latest copy of the preprocessed content store from the `govuk-data-infrastructure-integration` [S3 bucket](https://s3.console.aws.amazon.com/s3/buckets/govuk-data-infrastructure-integration?region=eu-west-1&prefix=knowledge-graph/&showversions=false)
2. Copy it to `data/raw/` directory of this repo and rename it `preprocessed_content_store.csv.gz`
3. It's best to run the script in a virtual environment. To set one up, run in the top level directory of this repo `python3 -m venv venv`. Once you've done that (or if you already have one) , run `source venv/bin/activate` to enter it
4. If you're running this for the first time, install requirements by running `pip install -r requirements.txt` (or `pip3 install -r requirements.txt`)
5. If you're running this for the first time, install spacy modules `python -m spacy download en_core_web_sm`
6. If you're running this for the first time, install nltk modules (in a python terminal) 
   ```
   python
   >>> import nltk
   >>> nltk.download('stopwords')
   >>> exit()
   ```
7. Run the script `python -m src.make_features.extract_subject_verb_object_from_content_titles` (or `python3 -m src.make_features.extract_subject_verb_object_from_content_titles`). This can take quite a long time.
8. Go and make a cup of tea or something.
9. When it's completed, there will be 3 files in the `/data/processed` directory, `entities.json`, `objects.json` and `verbs.json`

### Part 2. Generating new page popularity data for SVO Autocomplete

(Credit where due: this was made by Avision Ho with very few modifications, see original in src/notebooks/entities-synonyms)
If the output files are too big to be checked into git, you can alter the number of output files in `02_ranking_suggestions`

1. Ensure you have already generated the SVO data (Part 1)
2. Run `python -m src.make_features.svo_ranking.01_download_bq_data`
3. Run `python -m src.make_features.svo_ranking.02_ranking_suggestions`. This will output the files `svo_ranking_1.csv`, `svo_ranking_2.csv`, `svo_ranking_3.csv`, `svo_ranking_4.csv` and `svo_ranking_5.csv` into `data/processed`


### Part 3. Generating synonym data for SVO Autocomplete

(Credit where due: this was made by Avision Ho with very few modifications, see original in src/notebooks/entities-synonyms)

1. Ensure you have already generated the SVO data (Part 1)
2. Run `python -m src.make_features.svo_synonyms.01_preprocess_content_store`. (see caveats [here](src/make_features/README.MD))
3. Run `python -m src.make_features.svo_synonyms.02_train_word2vec_for_cbow_embeddings`.
4. Run `python -m src.make_features.svo_synonyms.03_cbow_synonyms`. This will output the files `entities_synonyms_cbow.json` and `objects_synonyms_cbow.json` into `data/processed`

### Part 4. Copy the data

When you've run all this, copy the output of each part (see the individual parts for the filenames) into the top level directory of `search-autocomplete-api`