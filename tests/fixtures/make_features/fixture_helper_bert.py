import pytest
import pandas as pd


@pytest.fixture()
def df_word_embeddings():
    return pd.DataFrame(data={'word': ['read', '##tik', '903', 'update'],
                              0: [0.2, 0.5, -0.1, -0.5],
                              1: [-0.7, 1.3, 0.3, -1 - 2],
                              2: [-0.1, 0.6, 0.3, 0.9]})


@pytest.fixture()
def df_similar_words():
    return pd.DataFrame(data={'word': ['update', '903', '##tik', 'read'],
                              'synonym': ['read', '##tik', '903', 'update'],
                              'cosine_similarity_score': [0.819478, 0.786616, 0.786616, 0.819478]})


@pytest.fixture()
def df_similar_words_clean():
    return pd.DataFrame(data={'word': ['read', 'update'],
                              'synonym': ['update', 'read'],
                              'cosine_similarity_score': [0.819478, 0.819478]})
