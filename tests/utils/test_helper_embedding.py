import src.utils.helper_embedding as f
import pytest


def test_reshape_df(df_embedding_mess, df_embedding_clean):
    df = f.reshape_df(df=df_embedding_mess,
                      col_name='embedding')
    assert df.equals(df_embedding_clean)


def test_calculate_cosine_similarity(vectors, vectors_cos_sim):
    with pytest.raises(TypeError):
        f.calculate_cosine_similarity(a=vectors['a'], b=vectors['c'])
    with pytest.raises(ValueError):
        f.calculate_cosine_similarity(a=vectors['a'], b=vectors['d'])
    assert f.calculate_cosine_similarity(a=vectors['a'],
                                         b=vectors['b']) == vectors_cos_sim


def test_extract_cosine_similarity(df_embedding_clean, series_cos_sim):
    series = f.extract_cosine_similarity(df=df_embedding_clean,
                                         word='sat',
                                         col_embedding='embedding')
    series = round(number=series, ndigits=6)
    assert series.equals(series_cos_sim)


def test_get_embedding_synonyms(df_embedding_clean, similar_words):
    assert f.get_embedding_synonyms(df=df_embedding_clean,
                                    word='sat',
                                    col_embedding='embedding',
                                    threshold=0.65) == similar_words['bow']
