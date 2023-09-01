from fhir_utils.utils import json_to_dict
from fhir_utils.fhir.patient.parsers import fhir_to_dict
from fhir_utils.fhir.patient.resource import Patient
from fhir_utils.fhir.merge import compare_resources
from dataclasses import replace, is_dataclass
import pprint


pp = pprint.PrettyPrinter(indent=4)

patient_json = json_to_dict("/home/thiagotrabach/tmp/patient_sample.json")
patient_json2 = json_to_dict("/home/thiagotrabach/tmp/patient_sample2.json")


patient = fhir_to_dict(patient_json, "vitacare")
patient2 = fhir_to_dict(patient_json2, "vitacare")


gabriela = Patient(name = patient["name"],
                   cpf = patient["identifiers"]["tax"],
                   birth_date = patient["birth_date"],
                   birth_country = "B",
                   source ="vitai",
                   mother = patient["mother"],
                   father = patient["father"],
                   gender = patient["gender"])

gabriela2 = Patient(name = patient2["name"],
                   cpf = patient2["identifiers"]["tax"],
                   birth_date = patient2["birth_date"],
                   birth_country = "B",
                   father = "Deus",
                   source ="vitai" ,
                   gender = patient2["gender"],
                   deceased = True,
                   active = False)


#print(compare_resources(gabriela, gabriela2))
pp.pprint(gabriela.compare(gabriela2))
print()
abc = gabriela.merge(gabriela2, force_invalid_merge=True)
pp.pprint(abc)
#print(gabriela)
#print(replace(gabriela2, name = "Thiago", birth_date = "1988-01-18"))
#print(is_dataclass(gabriela))
