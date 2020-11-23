import pytest
from pandas import DataFrame, Series


@pytest.fixture()
def df_embedding_mess():
    return DataFrame(data=[[0.15, 0.66, 0.78],
                           [0.34, 0.12, 0.03],
                           [0.49, 0.32, 0.77]],
                     columns=['cat', 'sat', 'mat'])


@pytest.fixture()
def df_embedding_clean():
    return DataFrame(data=[['cat', [0.15, 0.34, 0.49]],
                           ['sat', [0.66, 0.12, 0.32]],
                           ['mat', [0.78, 0.03, 0.77]]],
                     columns=['word', 'embedding'])


@pytest.fixture()
def vectors():
    return {'a': [0.10, 0.55, 0.68],
            'b': [0.37, 0.60, 0.91],
            'c': [None, 0.47, None],
            'd': [0.45, 0.59, 0.95, 0.66]}


@pytest.fixture()
def vectors_cos_sim():
    return 0.972877241875058


@pytest.fixture()
def series_cos_sim():
    return Series(data=[0.648909, 1.000000, 0.938497],
                  index=['cat', 'sat', 'mat'],
                  name='embedding')


@pytest.fixture()
def similar_words():
    return {'bow': ['mat']}
