

def fhir_to_dict(fhir_json: str, source: str) -> dict:
    # Extract identifiers
    identifiers = {}
    for identifier in fhir_json["identifier"]:
        identifiers[identifier["type"]["coding"][0]["code"].lower()] =  identifier["value"]

    # Extract extensions
    birth_city = ""
    birth_country = ""
    ethnicity = ""
    mother = ""
    father = ""
    nationality = ""
    naturalization = ""
    protected_person = ""
    register_quality = ""
    race = ""
    
    for extension in fhir_json["extension"]:
        match extension["url"]:
            case "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRQualidadeCadastroIndividuo-1.0":
                register_quality = extension["valuePositiveInt"]
            case "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRParentesIndividuo-1.0":
                match extension["extension"][0]["valueCode"]:
                    case "mother":
                        mother = extension["extension"][1]["valueHumanName"]["text"]
                    case "father":
                        father = extension["extension"][1]["valueHumanName"]["text"]
                    case _:
                        pass
            case "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRRacaCorEtnia-1.0":
                for element in extension["extension"]:
                    match element["url"]:
                        case "race":
                            race = element["valueCodeableConcept"]["coding"][0]["code"]
                        case "indigenousEthnicity":
                            ethnicity = element["valueCodeableConcept"]["coding"][0]["code"]
                        case _:
                            pass
            case "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRMunicipio-1.0":
                birth_city = extension["valueCodeableConcept"]["coding"][0]["code"]
            case "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRPais-1.0":
                birth_country = extension["valueCodeableConcept"]["coding"][0]["code"]
            case "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRNacionalidade":
                nationality = extension["valueCodeableConcept"]["coding"][0]["code"]
            case "https://rnds-fhir.saude.gov.br/CodeSystem/BRNaturalizacao-1.0":
                # TODO: add parser for naturality
                pass
            case "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRIndividuoProtegido-1.0":
                protected_person = extension["valueBoolean"]
            case _:
                pass

    return {"active": fhir_json["active"] if "active" in fhir_json.keys() else "",
            "address": fhir_json["address"] if "address" in fhir_json.keys() else "",
            "birth_city": birth_city,
            "birth_country": birth_country,
            "birth_date": fhir_json["birthDate"] if "birthDate" in fhir_json.keys() else "",
            "deceased": fhir_json["deceasedBoolean"] if "deceasedBoolean" in fhir_json.keys() else "",
            "gender": fhir_json["gender"] if "gender" in fhir_json.keys() else "",
            "cpf": identifiers["tax"] if "tax" in identifiers.keys() else "",
            "cns": identifiers["hc"] if "hc" in identifiers.keys() else "",
            "name": fhir_json["name"][0]["text"] if "name" in fhir_json.keys() else "",
            "nationality": nationality,
            "naturalization": naturalization,
            "mother": mother,
            "father": father,
            "protected_person": protected_person,
            "race": race,
            "ethnicity": ethnicity,
            "register_quality": register_quality,
            "telecom":  fhir_json["telecom"] if "telecom" in fhir_json.keys() else "",
            "_source": source,
            "_last_updated": ""
            }
            