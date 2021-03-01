import os
import json
import numpy as np
from annoy import AnnoyIndex


DIR_PROCESSED = os.getenv('DIR_DATA_PROCESSED')
with open('src/utils/config_annoy.json') as file_json:
    settings = json.load(fp=file_json)

# select which embeddings you are going to analyse
embedding_type = 'dgi_use_128'

# f is the length of embedding vector to be used
# f is the length of the vectors, aka 'embedding dimension'
f = settings[embedding_type]['embedding_dim']
# load a previously trained Annoy Index (the one you saved two lines up)
u = AnnoyIndex(f=f, metric='angular')
u.load(fn=DIR_PROCESSED + '/' + settings[embedding_type]['ann_index'])


def get_cosine_from_similarity(similarity, dp=4):
    """
    Converts the similarity distance metric into a cosine of the angle between the vectors

    Annoy uses Euclidean distance of normalized vectors for its angular distance,
    which for two vectors u,v is equal to sqrt(2(1-cos(u,v)))

    Returns a value between 0 and 1, a "similarity score" where 0 is not similar at all
    and 1 is practically identical
    """
    cosine_angle = 1 - (similarity**2) / 2
    cosine_angle = round(number=cosine_angle, ndigits=dp)
    return cosine_angle


def print_cosine_and_texts(df, text_idx, n_docs=2, max_length_string=1000):
    """
    Print out details of each query document and the best match.
    References:
        - https://github.com/alphagov/govuk-content-similarity/blob/main/src/utils/embedding_utils.py#L138

    Have not written tests for this because requires:
        - Building a dataset of text
        - Computing document embeddings
        - Building an Annoy Index
    """

    results = np.array(u.get_nns_by_item(i=text_idx, n=n_docs, include_distances=True))

    print("----")
    print('Index: ' + str(text_idx))
    print("----")
    print('query doc: ' + df['content_id'][results[0, 0]])
    print(f"page path: https://www.gov.uk{df['base_path'][results[0, 0]]}")
    print('date: ' + df['first_published_at'][results[0, 0]][:10])
    print("----")
    print(df['doc_text'][results[0, 0]][:max_length_string])
    print("----")

    print('\n similar content: \n')

    for i in range(1, n_docs):
        cosine_angle = get_cosine_from_similarity(similarity=results[1, i], dp=2)
        df_text = df.iloc[int(results[0, i])]

        print('Best match: ' + df_text['content_id'])
        print(f"Page path: https://www.gov.uk{df_text['base_path']}")
        print('date: ' + df_text['first_published_at'][:10])
        print("----")
        print(df_text['doc_text'][:max_length_string])
        print(f'Similarity score: {cosine_angle}')
