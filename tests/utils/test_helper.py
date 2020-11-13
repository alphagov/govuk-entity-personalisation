from src.utils.helper import get_n_word_strings


def test_get_n_word_strings(variable_word_strings, two_word_strings):
    assert get_n_word_strings(terms=variable_word_strings, n=2) == two_word_strings
