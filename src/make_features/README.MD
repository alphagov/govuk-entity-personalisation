# Subject Verb Object Autocomplete

These scripts are part of the process of extracting subject verb object relationships between words in content item titles.

### Prerequisites

* virtualenv running python 3.7 (why 3.7? The version of Gensim we're using is not tested beyond it)

### Generating new SVO data for SVO Autocomplete

1. Download the latest copy of the preprocessed content store from the `govuk-data-infrastructure-integration` [S3 bucket](https://s3.console.aws.amazon.com/s3/buckets/govuk-data-infrastructure-integration?region=eu-west-1&prefix=knowledge-graph/&showversions=false)
2. Copy it to `data/processed/` directory of this repo and rename it `preprocessed_content_store.csv`
3. It's best to run the script in a virtual environment. To set one up, run in the top level directory of this repo `python3 -m venv venv`. Once you've done that (or if you already have one) , run `source venv/bin/activate` to enter it
4. If you're running this for the first time, install requirements by running `pip install -r requirements.txt` (or `pip3 install -r requirements.txt`)
5. If you're running this for the first time, install spacy modules `python -m spacy download en_core_web_sm`
6. Run the script `python -m src.make_features.extract_subject_verb_object_from_content_titles` (or `python3 -m src.make_features.extract_subject_verb_object_from_content_titles`). This can take quite a long time and will require at least 60GB of memory
7. Go and make a cup of tea or something.
8. When it's completed, there will be 3 files in the `/data/processed` directory, `entities.json`, `objects.json` and `verbs.json`

### Generating new page popularity data for SVO Autocomplete

TBC

### Generating synonym data for SVO Autocomplete

TBC

