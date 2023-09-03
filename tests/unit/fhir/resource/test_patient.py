import pytest
from datetime import datetime
from fhir_utils.fhir.patient.resource import Patient


def test_format_cpf():
    patient = Patient(source="smsrio", name="John Doe", cpf="123.456.789-00", gender="male", birth_date="1990-01-01", birth_country="B")
    patient.format_cpf()
    assert patient.cpf == "12345678900"

def test_format_cns():
    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", cns="1234567890123-45")
    patient.format_cns()
    assert patient.cns == "123456789012345"

def test_format_name():
    patient = Patient(source="smsrio", name="  john  doe5 ", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B")
    formatted_name = patient.format_name(patient.name)
    assert formatted_name == "John Doe"

def test_format_cep():
    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", address=[{"postalCode": "12345-678"}])
    patient.format_cep()
    assert patient.address[0]["postalCode"] == "12345678"

def test_format_phone():
    # clean numeric chars for phone
    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", telecom=[{"system": "phone", "value": "+55 (21) 3456-7890"}])
    assert patient.telecom[0]["value"] == "552134567890"

    # complement phone with country and state code (rio de janeiro)
    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", telecom=[{"system": "phone", "value": "3456-7890"}])
    assert patient.telecom[0]["value"] == "552134567890"

    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", telecom=[{"system": "phone", "value": "93456-7890"}])
    assert patient.telecom[0]["value"] == "5521934567890"

    # complement phone with country
    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", telecom=[{"system": "phone", "value": "213456-7890"}])
    assert patient.telecom[0]["value"] == "552134567890"

    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", telecom=[{"system": "phone", "value": "2193456-7890"}])
    assert patient.telecom[0]["value"] == "5521934567890"

    # complement phone with country removing zero of state code
    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", telecom=[{"system": "phone", "value": "0213456-7890"}])
    assert patient.telecom[0]["value"] == "552134567890"

    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", telecom=[{"system": "phone", "value": "02193456-7890"}])
    assert patient.telecom[0]["value"] == "5521934567890"

    # multiple phones
    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", telecom=[{"system": "phone", "value": "+55 (21) 3456-7890"},
                                                                                                                                      {"system": "phone", "value": "+55 (21) 93456-7890"}])
    assert patient.telecom[0]["value"] == "552134567890" and patient.telecom[1]["value"] == "5521934567890"


def test_check_cpf():
    patient = Patient(source="smsrio", name="John Doe", cpf="878.776.698-10", gender="male", birth_date="1990-01-01", birth_country="B")
    assert patient.check_cpf() == True

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B")
    patient.check_cpf()
    assert patient.check_cpf() == False
