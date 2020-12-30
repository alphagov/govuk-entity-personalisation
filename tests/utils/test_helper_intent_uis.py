import src.utils.helper_intent_uis as f


def test_get_linguistic_features(text_pos_input, text_pos_output):
    assert f.get_linguistic_features(txt=text_pos_input) == text_pos_output


def test_get_linguistic_dict_to_df(text_pos_input, df_pos_output):
    df = f.get_linguistic_dict_to_df(txt=text_pos_input, linguistic_feature='pos')
    assert df.equals(df_pos_output)
