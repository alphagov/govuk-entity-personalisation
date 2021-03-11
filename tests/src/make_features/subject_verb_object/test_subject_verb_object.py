import pytest
from src.make_features.subject_verb_object.content import Title
import spacy
nlp = spacy.load("en_core_web_sm")

def assert_extracted_svo_matches_expected(title, actual):
    title.subject_object_triples(debug=True)
    print("results")
    for triple in title.subject_object_triples():
        print(f"subject: {triple.subject}")
        print(f"verb: {triple.verb}")
        print(f"object: {triple.object}")
    assert len(title.subject_object_triples()) == len(actual['triples'])
    for index, triple in enumerate(actual['triples']):
        assert title.subject_object_triples()[index].cypher_subject() == triple['subject']
        assert title.subject_object_triples()[index].cypher_verb() == triple['verb']
        assert title.subject_object_triples()[index].cypher_object() == triple['object']

def assert_svo_processor_extracts_correct_svo(fixture):
    title = Title(fixture['title'], nlp)
    assert_extracted_svo_matches_expected(title, fixture)

def test_apply_test_trace_support_payment_svo_processor(apply_test_trace_support_payment):
    assert_svo_processor_extracts_correct_svo(apply_test_trace_support_payment)

def test_apply_eu_settlement_scheme_svo_processor(apply_eu_settlement_scheme):
    assert_svo_processor_extracts_correct_svo(apply_eu_settlement_scheme)

def test_apply_uk_passport_svo_processor(apply_uk_passport):
    assert_svo_processor_extracts_correct_svo(apply_uk_passport)

def test_get_child_passport_svo_processor(get_child_passport):
    assert_svo_processor_extracts_correct_svo(get_child_passport)

def test_track_passport_application_svo_processor(track_passport_application):
    assert_svo_processor_extracts_correct_svo(track_passport_application)

def test_renew_driving_licence_svo_processor(renew_driving_licence):
    assert_svo_processor_extracts_correct_svo(renew_driving_licence)

def test_apply_adopt_child_svo_processor(apply_adopt_child):
    assert_svo_processor_extracts_correct_svo(apply_adopt_child)

def test_sign_in_universal_credit_svo_processor(sign_in_universal_credit):
    assert_svo_processor_extracts_correct_svo(sign_in_universal_credit)

def test_pay_dartford_crossing_charge_svo_processor(pay_dartford_crossing_charge):
    assert_svo_processor_extracts_correct_svo(pay_dartford_crossing_charge)


