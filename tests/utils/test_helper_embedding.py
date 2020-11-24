import src.utils.helper_embedding as f


def test_reshape_df(df_embedding_mess, df_embedding_clean):
    df = f.reshape_df(df=df_embedding_mess,
                      col_name='embedding')
    assert df.equals(df_embedding_clean)
