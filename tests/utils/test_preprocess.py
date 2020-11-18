import src.utils.preprocess as f


def test_get_n_word_strings(variable_word_strings, two_word_strings):
    assert f.get_n_word_strings(terms=variable_word_strings, n=2) == two_word_strings


def test_scrub_stopwords(text, text_stopword):
    assert f.scrub_stopwords(txt=text,
                             lib_sw='sklearn') == text_stopword['sklearn']
    assert f.scrub_stopwords(txt=text,
                             lib_sw='nltk') == text_stopword['nltk']
    assert f.scrub_stopwords(txt=text,
                             lib_sw='spacy') == text_stopword['spacy']
    assert f.scrub_stopwords(txt=text,
                             lib_sw='gensim') == text_stopword['gensim']


def test_lemmatise_text(text, text_lemmatise):
    assert f.lemmatise_text(txt=text,
                            lib_l='nltk') == text_lemmatise['nltk']
    assert f.lemmatise_text(txt=text,
                            lib_l='spacy') == text_lemmatise['spacy']


def test_clean_text(text, text_clean):
    assert f.clean_text(txt=text,
                        lib_sw='nltk',
                        lib_l='nltk') == text_clean['nltk']
    assert f.clean_text(txt=text,
                        lib_sw='spacy',
                        lib_l='spacy') == text_clean['spacy']
