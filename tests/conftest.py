import pytest


pytest_plugins = [
    "tests.fixtures.utils.fixture_helper_synonym",
    "tests.fixtures.utils.fixture_preprocess",
    "tests.fixtures.utils.fixture_helper_embedding",
    "tests.fixtures.utils.fixture_helper_intent_uis",
    "tests.fixtures.make_features.fixture_helper_bert",
]


@pytest.fixture()
def text():
    return "Following mice attacks, caring farmers were marching to Delhi for better living conditions. "\
           + "Delhi police on Tuesday fired water cannons and teargas shells at protesting farmers as "\
           + "they tried to break barricades with their cars, automobiles and tractors."


@pytest.fixture()
def text_misspell():
    return {'sentence': "whereis th elove heHAd dated forImuch of thEPast who couqdn'tread in sixtgrade and ins pired him",  # noqa: E501
            'document': "Goid morning Dr. Adams. The patient is w8iting for you in room njmbqr 3."}
