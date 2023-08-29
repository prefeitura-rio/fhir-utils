

def fhir_to_dict(fhir_json: str, source: str) -> dict:
    # Extract identifiers
    identifiers = []
    for identifier in fhir_json["identifier"]:
        identifiers.append({"code": identifier["type"]["coding"][0]["code"],
                            "value": identifier["value"]})

    # Extract extensions
    parents = []
    race_ethnicity = {"race":"", "indigenous_ethnicity":""}

    # TODO: add case for other extensions
    for extension in fhir_json["extension"]:
        match  extension["extension"][0]["url"]:
            case "relationship":
                parents.append({"code": extension["extension"][0]["valueCode"],
                                "name": extension["extension"][1]["valueHumanName"]["text"]
                                })
            case "race":
                race_ethnicity.update({"race": extension["extension"][0]["valueCodeableConcept"]["coding"][0]["code"]})
            case _:
                pass

    return {"data": {"active": fhir_json["active"] if "active" in fhir_json.keys() else "",
                     "address": fhir_json["address"] if "address" in fhir_json.keys() else "",
                     "birth_city": "",
                     "birth_country": "",
                     "birth_date": fhir_json["birthDate"] if "birthDate" in fhir_json.keys() else "",
                     "deceased": fhir_json["deceasedBoolean"] if "deceasedBoolean" in fhir_json.keys() else "",
                     "gender": fhir_json["gender"] if "gender" in fhir_json.keys() else "",
                     "identifiers": identifiers,
                     "name": fhir_json["name"][0]["text"] if "name" in fhir_json.keys() else "",
                     "nationality": "",
                     "naturalization": "",
                     "parents": parents,
                     "protected_person": "",
                     "race_ethnicity": race_ethnicity,
                     "register_quality": "",
                     "self.telecom":  fhir_json["telecom"] if "telecom" in fhir_json.keys() else ""
                    },
            "source": source
            }
            