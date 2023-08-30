from fhir_utils.utils import json_to_dict
from fhir_utils.fhir.patient.parsers import fhir_to_dict
from fhir_utils.fhir.patient.resource import Patient
from dataclasses import asdict
from fhir_utils.fhir.utils import compare_resources

patient_json = json_to_dict("/home/thiagotrabach/tmp/patient_sample.json")

patient = fhir_to_dict(patient_json, "vitacare")

gabriela = Patient(name = patient["data"]["name"],
                   cpf = patient["data"]["identifiers"]["tax"],
                   birth_date = patient["data"]["birth_date"],
                   source ="vitai" )

gabriela2 = Patient(name = patient["data"]["name"],
                   cpf = patient["data"]["identifiers"]["tax"],
                   birth_date = patient["data"]["birth_date"],
                   source ="vitacare" )

print(compare_resources(gabriela, gabriela2))


