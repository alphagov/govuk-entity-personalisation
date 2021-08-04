import pytest


@pytest.fixture()
def variable_word_strings():
    return ['this is a',
            'varying length list of strings',
            'which we want to use for testing purposes.',
            'hopefully',
            'it works',
            'well',
            'and does not',
            'fail badly',
            ':sob face:']


@pytest.fixture()
def two_word_strings():
    return ['it works', 'fail badly', ':sob face:']


@pytest.fixture()
def text_stopword():
    return {'sklearn': "Following mice attacks, caring farmers marching Delhi better living conditions. Delhi police "
                       + "Tuesday fired water cannons teargas shells protesting farmers tried break barricades "
                       + "cars, automobiles tractors.",
            'nltk': "Following mice attacks, caring farmers marching Delhi better living conditions. Delhi police "
                    + "Tuesday fired water cannons teargas shells protesting farmers tried break barricades "
                    + "cars, automobiles tractors.",
            'spacy': "Following mice attacks, caring farmers marching Delhi better living conditions. Delhi police "
                     + "Tuesday fired water cannons teargas shells protesting farmers tried break barricades "
                     + "cars, automobiles tractors.",
            'gensim': "Following mice attacks, caring farmers marching Delhi better living conditions. Delhi police "
                      + "Tuesday fired water cannons teargas shells protesting farmers tried break barricades "
                      + "cars, automobiles tractors."}


@pytest.fixture()
def text_lemmatise():
    return {'nltk': "Following mouse attack , caring farmer were marching to Delhi for better living condition . "
                    + "Delhi police on Tuesday fired water cannon and teargas shell at "
                    + "protesting farmer a they tried to break barricade with their car , automobile and tractor .",
            'spacy': "follow mice attack , care farmer be march to Delhi for well living condition . "
                     + "Delhi police on Tuesday fire water cannon and teargas shell at protest farmer "
                     + "as -PRON- try to break barricade with -PRON- car , automobile and tractor ."}


@pytest.fixture()
def text_clean():
    return {'nltk': "following mouse attack caring farmer marching delhi better living condition delhi police tuesday "
                    + "fired water cannon teargas shell protesting farmer tried break barricade car automobile tractor",
            'spacy': "follow mice attack care farmer march delhi better living condition delhi police tuesday "
                     + "fire water cannon teargas shell protest farmer try break barricade car automobile tractor"}


@pytest.fixture()
def text_spell_correct():
    return {'sentence': "whereas the love heAd dated for much of thE Past who couldn't read in six grade and inspired him",  # noqa: E501
            'document': "Good morning Or Adams. The patient is writing for you in room number 3."}
