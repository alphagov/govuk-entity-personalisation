import src.make_features.helper_bert as f
import pandas.testing as pdt


def test_get_similar_words(df_word_embeddings, df_similar_words):
    df_in = f.get_similar_words(df=df_word_embeddings,
                                col_word='word',
                                similarity_score=0.7).reset_index(drop=True)
    df_out = df_similar_words.reset_index(drop=True)
    pdt.assert_frame_equal(left=df_in, right=df_out)


def test_clean_similar_words(df_similar_words, df_similar_words_clean):
    df_in = f.clean_similar_words(df=df_similar_words,
                                  col_word_synonyms_score=['word',
                                                           'synonym',
                                                           'cosine_similarity_score']).reset_index(drop=True)
    df_out = df_similar_words_clean.reset_index(drop=True)
    pdt.assert_frame_equal(left=df_in, right=df_out)
