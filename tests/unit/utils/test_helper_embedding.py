import src.utils.helper_embedding as f
import pytest
from numpy import array_equal, round_


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


def test_extract_paragraphs(content_embed):
    assert f.extract_paragraphs(txt=content_embed['details_html']) == content_embed['details']


def test_get_document_embedding(content_embed):
    input_embed = f.get_document_embedding(txt=content_embed['details'])
    input_embed = round_(a=input_embed, decimals=4)
    output_embed = round_(a=content_embed['embedding'], decimals=4)
    assert array_equal(input_embed, output_embed)


def test_get_paragraphs_and_embeddings(content_embed):
    input_id, input_details, input_embed = f.get_paragraphs_and_embeddings(id=content_embed['id'],
                                                                           txt=content_embed['details_html'])
    input_embed = round_(a=input_embed, decimals=4)
    output_embed = round_(a=content_embed['embedding'], decimals=4)
    output_details = ' '.join(content_embed['details'])
    assert input_id == content_embed['id']
    assert input_details, output_details
    assert array_equal(input_embed, output_embed)
