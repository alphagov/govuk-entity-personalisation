# `src` package

For folder usage, please refer to the documentation [here](../docs/structure/README.md#src-package).

Note, for the `config_annoy.json` file, sources for each embedding is as follows:
```json
{
    # https://github.com/alphagov/govuk-content-similarity/blob/embeddings-nearest-neighbours/notebooks/sbert_sentence_transformers.py
    'dilbert': {'embeddings': 'embeddings_distilbert_base_df.csv',
                'text': 'text_distilbert_base_df.csv',
                'embedding_dim': 768,
                'ann_index': 'sbert.ann'},
    # https://github.com/alphagov/govuk-content-similarity/blob/embeddings-nearest-neighbours/notebooks/universal_sentence_encoder.py
    'use_2000': {'embeddings': 'embeddings_use_large_2000_df.csv',
                 'text': 'text_use_large_2000_df.csv',
                 'embedding_dim': 512,
                 'ann_index': 'use_2000.ann'},
    # 02_dgi_embeddings.py
    'dgi_use_128': {'embeddings': 'dgi_embeddings_df.csv',
                    'text': 'text_use_large_2000_df.csv',
                    'embedding_dim': 128,
                    'ann_index': 'dgi_use_128.ann'}
}
```
