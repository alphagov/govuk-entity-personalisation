import pytest


@pytest.fixture()
def terms_synonyms():
    return {'finance': ['back', 'refinance', 'fund', 'pay', 'seed'],
            'state': ['province', 'land', 'American state', 'Australian state',
                      'eparchy', 'country', 'territorial division', 'commonwealth',
                      'Soviet Socialist Republic', 'administrative district',
                      'Italian region', 'Canadian province', 'administrative division'],
            'form': ['main entry word', 'plural form', 'plural', 'singular', 'word form',
                     'acronym', 'etymon', 'stem', 'abbreviation', 'theme', 'root', 'ghost word',
                     'citation form', 'descriptor', 'entry word', 'word', 'root word', 'base',
                     'singular form', 'signifier', 'radical']}
