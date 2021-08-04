import pytest
from src.make_features.subject_verb_object.content import Title
from src.make_features.subject_verb_object.utils import spacy_model
nlp = spacy_model()


def assert_extracted_entity_matches_expected(title, actual):
    title.entities(debug=True)
    print("results")
    for entity in title.entities():
        print(f"entity: {entity.entity}")
    assert len(title.entities()) == len(actual['entities'])
    for index, triple in enumerate(actual['entities']):
        assert title.entities()[index].cypher_entity() == triple['entity']


def assert_entity_processor_extracts_correct_entities(fixture):
    title = Title(fixture['title'], nlp)
    assert_extracted_entity_matches_expected(title, fixture)


def test_passports_and_emergency_travel_documents_entity_processor(passports_and_emergency_travel_documents):
    assert_entity_processor_extracts_correct_entities(passports_and_emergency_travel_documents)


def test_advisory_credit_committee_entity_processor(advisory_credit_committee):
    assert_entity_processor_extracts_correct_entities(advisory_credit_committee)


def test_emissions_testing_svo_processor(emissions_testing):
    assert_entity_processor_extracts_correct_entities(emissions_testing)