from src.utils.helper_synonym import get_synonym_all


def test_get_synonym_all(terms_synonyms):
    assert get_synonym_all(terms=terms_synonyms.keys()) == terms_synonyms
