import src.utils.helper_intent_uis as f


def test_get_pos(text_pos_input, text_pos_output):
    assert f.get_pos(txt=text_pos_input) == text_pos_output
