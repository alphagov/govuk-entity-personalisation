import pytest

@pytest.fixture()
def apply_test_trace_support_payment():
    return {
        "title": "Apply for a Test and Trace Support Payment",
        "triples": [
            {
                "subject": "",
                "verb": "apply",
                "object": "support payment"
            }
        ]
    }


@pytest.fixture()
def apply_eu_settlement_scheme():
    return {
        "title": "Apply to the EU Settlement Scheme",
        "triples": [
            {
                "subject": "",
                "verb": "apply",
                "object": "eu settlement scheme"
            }
        ]
    }

@pytest.fixture()
def apply_uk_passport():
    return {
        "title": "Apply online for a UK passport",
        "triples": [
            {
                "subject": "",
                "verb": "apply",
                "object": "uk passport"
            }
        ]
    }

@pytest.fixture()
def get_child_passport():
    return {
        "title": "Get a passport for your child",
        "triples": [
            {
                "subject": "",
                "verb": "get",
                "object": "passport"
            },
            {
                "subject": "your",
                "verb": "passport",
                "object": "child"
            }
        ]
    }

@pytest.fixture()
def track_passport_application():
    return {
        "title": "Track your passport application",
        "triples": [
            {
                "subject": "",
                "verb": "track",
                "object": "passport application"
            }
        ]
    }

@pytest.fixture()
def renew_driving_licence():
    return {
        "title": "Renew your driving licence",
        "triples": [
            {
                "subject": "",
                "verb": "renew",
                "object": "driving licence"
            }
        ]
    }

@pytest.fixture()
def apply_adopt_child():
    return {
        "title": "Apply to adopt a child through your council",
        "triples": [
            {
                "subject": "",
                "verb": "apply",
                "object": "adopt"
            },
            {
                "subject": "",
                "verb": "adopt",
                "object": "child"
            }
        ]
    }

@pytest.fixture()
def sign_in_universal_credit():
    return {
        "title": "Sign in to your Universal Credit account",
        "triples": [
            {
                "subject": "your",
                "verb": "sign in",
                "object": "universal credit account"
            }
        ]
    }

@pytest.fixture()
def pay_dartford_crossing_charge():
    return {
        "title": "Pay the Dartford Crossing charge (Dart Charge)",
        "triples": [
            {
                "subject": "",
                "verb": "pay",
                "object": "dartford crossing charge"
            }
        ]
    }




