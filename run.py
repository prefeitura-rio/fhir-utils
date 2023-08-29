from fhir_utils.utils import json_to_dict
from fhir_utils.fhir.patient.parsers import fhir_to_dict

patient = json_to_dict("/home/thiagotrabach/tmp/patient_sample.json")

patient_clean = fhir_to_dict(patient, "vitacare")

print(patient_clean)


