from fhir_utils.utils import json_to_dict, save_to_json
from fhir_utils.fhir.patient.parsers import fhir_to_dict
from fhir_utils.fhir.patient.resource import Patient
from fhir_utils.fhir.merge import compare_resources
from dataclasses import replace, is_dataclass
from fhir_utils.healthcare_api import FastCRUD
import pprint
import os

# Parameters
PROJECT_ID = "rj-sms-dev"
LOCATION = "us-central1"
DATASET_RAW = "raw_layer"
FHIR_STORE_ID_RAW = "vitai"
SOURCE_RAW = "vitai"
DATASET_REFINED = "refined_layer"
FHIR_STORE_ID_REFINED = "rj-sms"
SOURCE_REFINED = "rj-sms"

# Inicializa as classes
health_api = FastCRUD(project_id= PROJECT_ID, location= LOCATION)

# Começa o fluxo de execução
# Carrega o novo registro
patient_raw_fhir = json_to_dict(os.path.join(os.path.dirname(__file__), 'tests/unit/fhir/resource/test_data', 'patient_data.json'))
patient_raw_dict = fhir_to_dict(patient_raw_fhir, source=SOURCE_RAW)
patient_raw = Patient(
    source = patient_raw_dict["_source"],
    name = patient_raw_dict["name"],
    cpf = patient_raw_dict["cpf"],
    gender = patient_raw_dict["gender"],
    birth_date = patient_raw_dict["birth_date"],
    birth_country = patient_raw_dict["birth_country"],
    cns = patient_raw_dict["cns"],
    active = patient_raw_dict["active"],
    address = patient_raw_dict["address"],
    birth_city = patient_raw_dict["birth_city"],
    deceased = patient_raw_dict["deceased"],
    nationality = patient_raw_dict["nationality"],
    naturalization = patient_raw_dict["naturalization"] ,
    mother = patient_raw_dict["mother"],
    father = patient_raw_dict["father"],
    protected_person = patient_raw_dict["protected_person"],
    race = patient_raw_dict["race"],
    ethnicity = patient_raw_dict["ethnicity"],
    telecom= patient_raw_dict["telecom"]
    )

# Check if patient already exists 
response = health_api.patient_search(
    dataset_id= DATASET_REFINED,
    fhir_store_id= FHIR_STORE_ID_REFINED,
    cpf= patient_raw.cpf)

print(f"Found {response['body']['total']} entrie(s) in {DATASET_REFINED}/{FHIR_STORE_ID_REFINED}")

if response["status_code"] == 200:

    if response["body"]["total"] > 0:

        print("Resource already exists. Starting merge process")

        # Load base resource to memory
        patient_refined_dict = fhir_to_dict(response["body"]["entry"][0]["resource"], source=SOURCE_REFINED)
        patient_refined = patient_raw = Patient(
            source = patient_refined_dict["_source"],
            name = patient_refined_dict["name"],
            cpf = patient_refined_dict["cpf"],
            gender = patient_refined_dict["gender"],
            birth_date = patient_refined_dict["birth_date"],
            birth_country = patient_refined_dict["birth_country"],
            cns = patient_refined_dict["cns"],
            active = patient_refined_dict["active"],
            address = patient_refined_dict["address"],
            birth_city = patient_refined_dict["birth_city"],
            deceased = patient_refined_dict["deceased"],
            nationality = patient_refined_dict["nationality"],
            naturalization = patient_refined_dict["naturalization"] ,
            mother = patient_refined_dict["mother"],
            father = patient_refined_dict["father"],
            protected_person = patient_refined_dict["protected_person"],
            race = patient_refined_dict["race"],
            ethnicity = patient_refined_dict["ethnicity"],
            telecom= patient_refined_dict["telecom"]
            )
        
        # Merge resources
        patient_merged = patient_refined.merge(patient_raw, force_invalid_merge= False)
        payload = patient_merged.to_fhir()
        
    else:
        print(f"Resource does not exists. Merge not needed")
        # Load raw resource to Healthcare API
        payload = patient_raw.to_fhir()

    response = health_api.patient_update(
        dataset_id= DATASET_REFINED,
        fhir_store_id= FHIR_STORE_ID_REFINED,
        cpf= patient_raw.cpf,
        payload= payload)
    
    if response["status_code"] == 200 or response["status_code"] == 201:
        print(f"SUCCESS: Resource uploaded to {DATASET_REFINED}/{FHIR_STORE_ID_REFINED}")
    else:
        print(f"FAIL: Resource not uploaded to {DATASET_REFINED}/{FHIR_STORE_ID_REFINED}")

else:
    print(f"FAIL: api returned code {response['status_code']}")


#
#
#
#patient_json = json_to_dict("/home/thiagotrabach/tmp/patient_sample.json")
#patient_json2 = json_to_dict("/home/thiagotrabach/tmp/patient_sample2.json")
#
#
#patient = fhir_to_dict(patient_json, "vitacare")
#patient2 = fhir_to_dict(patient_json2, "vitacare")
#
#
#gabriela = Patient(name = patient["name"],
#                   cpf = patient["identifiers"]["tax"],
#                   birth_date = patient["birth_date"],
#                   birth_country = "B",
#                   source ="vitai",
#                   mother = patient["mother"],
#                   father = patient["father"],
#                   gender = patient["gender"])
#
#gabriela2 = Patient(name = patient2["name"],
#                   cpf = patient2["identifiers"]["tax"],
#                   birth_date = patient2["birth_date"],
#                   birth_country = "B",
#                   father = "Deus",
#                   source ="vitai" ,
#                   gender = patient2["gender"],
#                   deceased = True,
#                   active = False)
#
#
#print(compare_resources(gabriela, gabriela2))
#pp.pprint(gabriela)
#pp.pprint(gabriela.compare(gabriela2) == {})
#print()
#gabriela_mergead = gabriela.merge(gabriela2, force_invalid_merge=True)
#pp.pprint(abc)
#print(gabriela)
#print(replace(gabriela2, name = "Thiago", birth_date = "1988-01-18"))
#print(is_dataclass(gabriela))
#pp.pprint(gabriela.to_fhir())
#patient = Patient(
#        source="smsrio",
#        name="John Doe",
#        cpf="878.776.698-10",
#        gender="male",
#        birth_date="2000-01-01",
#        birth_country="10",
#        cns="123456789012345",
#        active=True,
#        address=[{
#            "use": "home",
#            "type": "postal",
#            "line":  ["081", "SQN  BLOCO M", "604", "APARTAMENTO", "ASA NORTE"],
#            "city": "315780",
#            "state": "53",
#            "postalCode": "70752130"
#        }],
#        birth_city="315780",
#        deceased=False,
#        nationality="10",
#        naturalization="10",
#        mother="Jane Doe",
#        father="John Doe Sr.",
#        protected_person=False,
#        race="05",
#        ethnicity="X405",
#        telecom=[{
#            "system": "phone",
#            "value": "5521123456789",
#            "use": "home"
#        }]
#    )
#save_to_json(patient.to_fhir(), "/home/thiagotrabach/tmp/patient_test.json")