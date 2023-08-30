from fhir_utils.utils import json_to_dict
from fhir_utils.fhir.patient.parsers import fhir_to_dict
from fhir_utils.fhir.patient.resource import Patient
from fhir_utils.fhir.merge import compare_resources, merge_resource
from dataclasses import replace

patient_json = json_to_dict("/home/thiagotrabach/tmp/patient_sample.json")
patient_json2 = json_to_dict("/home/thiagotrabach/tmp/patient_sample2.json")


patient = fhir_to_dict(patient_json, "vitacare")
patient2 = fhir_to_dict(patient_json2, "vitacare")


gabriela = Patient(name = patient["name"],
                   cpf = patient["identifiers"]["tax"],
                   birth_date = patient["birth_date"],
                   source ="vitai" )

gabriela2 = Patient(name = patient2["name"],
                   cpf = patient2["identifiers"]["tax"],
                   birth_date = patient2["birth_date"],
                   father = "Deus",
                   source ="vitai" )


print(compare_resources(gabriela, gabriela2))
print()
print(replace(gabriela2, name = "Thiago", birth_date = "1988-01-18"))


