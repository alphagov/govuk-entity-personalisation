import pytest
from pandas import DataFrame, Series


@pytest.fixture()
def df_embedding_mess():
    return DataFrame(data=[[1, 0, 0],
                           [0, 1, 0],
                           [0, 0, 1]],
                     columns=['cat', 'sat', 'mat'])


@pytest.fixture()
def df_embedding_clean():
    return DataFrame(data=[['cat', [1, 0, 0]],
                           ['sat', [0, 1, 0]],
                           ['mat', [0, 0, 1]]],
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
def df_cos_sim():
    return Series(data=[0.0, 1.0, 0.0],
                  index=['cat', 'sat', 'mat'])
