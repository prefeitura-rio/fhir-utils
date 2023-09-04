import pytest
from datetime import datetime
from fhir_utils.fhir.patient.resource import Patient
from dataclasses import asdict


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
    assert patient.check_cpf() == False and "cpf" in patient._invalid_elements

def test_check_cns():
    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", cns="213321999239456", gender="male", birth_date="1990-01-01", birth_country="B")
    assert patient.check_cns() == True

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", cns="213321999", gender="male", birth_date="1990-01-01", birth_country="B")
    assert patient.check_cns() == False and "cns" in patient._invalid_elements

def test_check_birth_country():
    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B")
    assert patient.check_birth_country() == True

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="Brasil")
    assert patient.check_birth_country() == False and "birth_country" in patient._invalid_elements

def test_check_birth_date():
    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B")
    assert patient.check_birth_date() == True

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="01-01-1990", birth_country="B")
    assert patient.check_birth_date() == False and "birth_date" in patient._invalid_elements

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="2100-01-01", birth_country="B")
    assert patient.check_birth_date() == False and "birth_date" in patient._invalid_elements

def test_check_gender():
    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B")
    assert patient.check_gender() == True

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="m", birth_date="01-01-1990", birth_country="B")
    assert patient.check_gender() == False and "gender" in patient._invalid_elements

def test_check_address():
    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B",
                      address=[{"use": "home",
                                "type": "both",
                                "line": ["081",
                                          "SQN  BLOCO M",
                                          "604",
                                          "APARTAMENTO",
                                          "ASA NORTE"],
                                "city": "315780",
                                "state": "53",
                                "postalCode": "70752130"}])
    
    assert patient.check_address() == True

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B",
                      address=[{"use": "home",
                                "type": "both",
                                "line": ["RUA",
                                        "SQN  BLOCO M",
                                        "604"],
                                "city": "Rio de Janeiro",
                                "state": "RJ",
                                "postalCode": "7075230"}])
    assert patient.check_address() == False and "address" in patient._invalid_elements


def test_check_address():
    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B",
                      address=[{"use": "home",
                                "type": "both",
                                "line": ["081",
                                          "SQN  BLOCO M",
                                          "604",
                                          "APARTAMENTO",
                                          "ASA NORTE"],
                                "city": "315780",
                                "state": "53",
                                "postalCode": "70752130"}])
    
    assert patient.check_address() == True

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B",
                      address=[{"use": "home",
                                "type": "both",
                                "line": ["RUA",
                                        "SQN  BLOCO M",
                                        "604"],
                                "city": "Rio de Janeiro",
                                "state": "RJ",
                                "postalCode": "7075230"}])
    assert patient.check_address() == False and "address" in patient._invalid_elements

def test_check_telecom():
    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B",
                     telecom=[{"system": "phone",
                               "value": "552134567890",
                               "use": "home"}] )
    assert patient.check_telecom() == True

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B",
                     telecom=[{"system": "phone",
                               "value": "552134567890"}] )
    assert patient.check_telecom() == False and "telecom" in patient._invalid_elements

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B",
                     telecom=[{"system": "email",
                               "value": "abc.com",
                               "use": "home"}] )
    assert patient.check_telecom() == False and "telecom" in patient._invalid_elements

def test_calculate_register_quality():
    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B", deceased=False, active=True)
    assert patient.register_quality == 33

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B", deceased=False, active=True,
                     telecom=[{"system": "phone",
                               "value": "552134567890",
                               "use": "home"}])
    assert patient.register_quality == 38

    patient = Patient(source="smsrio", name="John Doe", cpf="1234567890", gender="male", birth_date="1990-01-01", birth_country="B", deceased=False, active=True,
                     telecom=[{"system": "",
                               "value": "552134567890",
                               "use": "home"}])
    assert patient.register_quality == 33

def test_compare():
    patient1 = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B")
    patient2 = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B")
    assert patient1.compare(patient2) == {}

    patient1 = Patient(source="smsrio", name="John", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B")
    patient2 = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B")
    assert patient1.compare(patient2) == {"values_changed": {"root.name": {"new_value": "John Doe", "old_value": "John"}}}

def test_merge():
    # valid resource
    patient = Patient(source="smsrio", name="John Doe", cpf="878.776.698-10", gender="male", birth_date="1990-01-01", birth_country="B", active= True, father = "Caetano")
    patient_new = Patient(source="smsrio", name="John Doe", cpf="878.776.698-10", gender="male", birth_date="1990-01-01", birth_country="B", active= False, mother = "Rita")
    
    expected_merge =  Patient(source="smsrio", name="John Doe", cpf="878.776.698-10", gender="male", birth_date="1990-01-01", birth_country="B", active= False, father= "Caetano", mother = "Rita")
    
    merged_patient = patient.merge(patient_new, force_invalid_merge=False)
    
    assert merged_patient == expected_merge

    # invalid resource
    patient = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", active= True, father = "Caetano")
    patient_new = Patient(source="smsrio", name="John Doe", cpf="12345678900", gender="male", birth_date="1990-01-01", birth_country="B", active= False, mother = "Rita")

    with pytest.raises(ValueError) as excinfo:  
        patient.merge(patient_new, force_invalid_merge=False) 
    assert str(excinfo.value) == "Can't merge invalid resource" 