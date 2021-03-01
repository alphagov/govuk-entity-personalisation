import pytest
import pandas as pd


@pytest.fixture()
def text_pos_input():
    return "Apple is looking at buying U.K. startup for $1 billion"


@pytest.fixture()
def text_pos_output():
    return {'pos': ['PROPN', 'AUX', 'VERB', 'ADP', 'VERB', 'PROPN', 'NOUN', 'ADP', 'SYM', 'NUM', 'NUM'],
            'tag': ['NNP', 'VBZ', 'VBG', 'IN', 'VBG', 'NNP', 'NN', 'IN', '$', 'CD', 'CD'],
            'dep': ['nsubj', 'aux', 'ROOT', 'prep', 'pcomp', 'compound', 'dobj', 'prep', 'quantmod', 'compound', 'pobj'],  # noqa: E501
            'lemma': ['Apple', 'be', 'look', 'at', 'buy', 'U.K.', 'startup', 'for', '$', '1', 'billion'],
            'stop': [False, True, False, True, False, False, False, True, False, False, False]}


@pytest.fixture()
def df_pos_output():
    return pd.DataFrame(data={"q3": ["Apple is looking at buying U.K. startup for $1 billion"] * 11,
                              "word_position": list(range(11)),
                              "pos": ["PROPN", "AUX", "VERB", "ADP", "VERB", "PROPN", "NOUN", "ADP", "SYM", "NUM", "NUM"]})  # noqa: E501
