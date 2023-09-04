# -*- coding: utf-8 -*-
from fhir_utils.utils import (
    capitalize_each_word,
    keep_alpha_characters,
    keep_numeric_characters,
    remove_wrong_whitespaces, 
    is_valid_cpf, 
    is_valid_date_format)
from fhir_utils.fhir.merge import compare_resources, merge_element
from dataclasses import dataclass, field, is_dataclass, replace
from datetime import datetime
import re
import logging


@dataclass
class Patient:
    source : str
    name : str
    cpf : str
    gender : str
    birth_date : str
    birth_country : str
    cns : str = ""
    active : bool = True
    address : str = ""
    birth_city : str = ""
    deceased : bool = False
    nationality : str = ""
    naturalization : str = ""
    mother : str = ""
    father : str = ""
    protected_person : bool = ""
    race: str = ""
    ethnicity : str = ""
    telecom : str = ""
    register_quality : float = field(init = False)
    _is_valid: bool = field(init = False)
    _invalid_elements: list = field(init = False)
    _resource_type : str = field(init = False)

    def __post_init__(self):
        # default values
        self._resource_type = "patient"
        self.telecom = [] if self.telecom == "" or self.telecom is None else self.telecom
        self.address = [] if self.address == "" or self.address is None  else self.address
        self._is_valid = True
        self._invalid_elements = []
        self.register_quality = 0

        # format values
        self.format_cpf()
        self.format_cns()
        self.name = self.format_name(self.name)
        self.mother = self.format_name(self.mother)
        self.father = self.format_name(self.father)
        self.format_cep()
        self.format_phone()

        # check if input is correct
        self.check_cpf()
        self.check_cns()
        self.check_birth_country()
        self.check_birth_date()
        self.check_gender()
        self.check_address()
        self.check_telecom()
        self.check_nationality
        self.check_race()
        self.check_ethnicity()

        # calculate register quality
        self.calculate_register_quality()

    def format_cpf(self):
        self.cpf = keep_numeric_characters(self.cpf)
    
    def format_cns(self):
        self.cns = keep_numeric_characters(self.cns)

    def format_name(self, name):
        name = remove_wrong_whitespaces(name)
        name = keep_alpha_characters(name)
        name = capitalize_each_word(name)
        return name
    
    def format_cep(self):
        if type(self.address) is list:
            for i, address in enumerate(self.address):
                try:
                    self.address[i]["postalCode"] = keep_numeric_characters(address["postalCode"])
                except:
                    pass

    def format_phone(self):
        # We assume that any phone without state code state are from Rio de Janeiro city
        if type(self.telecom) is list:
            for i, telecom in enumerate(self.telecom):
                if telecom["system"] == "phone":
                    phone = keep_numeric_characters(telecom["value"])
                    if phone[0] == "0": # zero on the left for state code
                        phone = phone[1:]
                    if 8 <= len(phone) <= 9: 
                        phone = f"5521{phone}" 
                    elif 10 <= len(phone) <= 11:
                        phone = f"55{phone}"
                        
                    self.telecom[i]["value"] = phone

    def check_cpf(self):
        if not is_valid_cpf(self.cpf):
            self._is_valid = False
            self._invalid_elements.append("cpf")
            return False
        else:
            return True

    def check_cns(self):
        if len(self.cns) > 0 and len(self.cns) != 15:
            self._is_valid = False
            self._invalid_elements.append("cns")
            return False
        else:
            return True
        
    def check_birth_country(self):
        if not 2 <= len(keep_numeric_characters(self.birth_country)) <= 3:
            self._is_valid = False
            self._invalid_elements.append("birth_country")
            return False
        else:
            return True

    def check_birth_date(self):
        is_valid = True
        if not is_valid_date_format(self.birth_date):
            is_valid = False
        elif datetime.strptime(self.birth_date, "%Y-%m-%d") > datetime.now():
            is_valid = False
        elif datetime.strptime(self.birth_date, "%Y-%m-%d") < datetime(1900, 1, 1):
            is_valid = False
        
        if is_valid:
            return True
        else:
            self._is_valid = False
            self._invalid_elements.append("birth_date")
            return False
    
    def check_gender(self):
        if self.gender not in ["male", "female", "unknown"]:
            self._is_valid = False
            self._invalid_elements.append("gender")
            return False
        else:
            return True

    def check_address(self):
        is_valid = True
        
        if type(self.address) is list:

            keys = ["use", "type", "line", "city", "state", "postalCode"]

            for i, address in enumerate(self.address):
                # if all must have keys are present
                if not all(key in address for key in keys):
                    is_valid = False
                # accepted values
                elif address["use"] not in ["home", "work", "temp", "old", "billing"]:
                    is_valid = False
                elif address["type"] not in ["postal", "physical", "both"]:
                    is_valid = False
                elif not 4 <= len(address["line"]) <= 5 or address["line"][0] not in ["008", "081"]:
                    is_valid = False
                elif len(keep_numeric_characters(address["city"])) != 6:
                    is_valid = False
                elif len(keep_numeric_characters(address["state"])) != 2:
                    is_valid = False
                elif len(keep_numeric_characters(address["postalCode"])) != 8:
                    is_valid = False

        if is_valid:
            return True
        else:
            self._is_valid = False
            self._invalid_elements.append("address")
            return False
             
    def check_telecom(self):
        # TODO: raise type error execption if not a list
        is_valid = True
        if type(self.telecom) is list:

            keys = ["system", "value", "use"]
            
            for i, telecom in enumerate(self.telecom):
                # if all must have keys are present
                if not all(key in telecom for key in keys):
                    is_valid = False
                # accepted values
                elif telecom["system"] not in ["phone", "fax", "email", "pager", "url", "sms", "other"]:
                    is_valid = False
                elif telecom["use"] not in ["home", "work", "temp", "old", "mobile"]:
                    is_valid = False
                elif telecom["system"] == "phone" and not 12 <= len(telecom["value"]) <=13: # ddi+ddd+phone
                    is_valid = False

                elif telecom["system"] == "email" and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", telecom["value"]):
                    is_valid = False
        
            if is_valid:
                return True
            else:
                self._is_valid = False
                self._invalid_elements.append("telecom")
                return False

    def check_race(self):
        if self.race != "" and len(self.race) != 2:
            self._is_valid = False
            self._invalid_elements.append("race")
            return False
        else:
            return True
        
    def check_ethnicity(self):
        if self.ethnicity != "" and len(self.ethnicity) != 4:
            self._is_valid = False
            self._invalid_elements.append("ethnicity")
            return False
        else:
            return True

    def check_nationality(self):
        if self.nationality not in ["B", "E", "N"]:
            self._is_valid = False
            self._invalid_elements.append("nationality")
            return False
        else:
            return True
        
    #def check_naturalization(self):
        # TODO: check natualization

    def calculate_register_quality(self):
        counter = 0

        quality_properties = ["name", "cpf", "gender", "birth_date", "birth_country", "cns",
                               "active", "address", "birth_city", "deceased", "nationality", 
                               "naturalization", "mother", "father", "protected_person", 
                               "race", "ethnicity","telecom"]

        for p in self.__dict__.items():
            if p[0] in quality_properties:
                if p[0] in ["address", "telecom"]:
                    if len(p[1]) > 0 and p[0] not in self._invalid_elements:
                        counter += 1
                elif p[1] != "" and p[1] != None and p[0] not in self._invalid_elements:
                    counter += 1

        self.register_quality = int(counter/len(quality_properties) * 100)


    def compare(self, new_resource):
        # compare current patient with another one
        if is_dataclass(new_resource):
            if new_resource._resource_type != "patient":
                raise TypeError("The new resource must be the same class")
        else:
            raise TypeError("The new resource must be the same class")

        return compare_resources(self, new_resource)

    def merge(self, new_resource, force_invalid_merge: False):
        # TODO: mode that discard invalid values

        # check if both resource are of the same type
        nr = new_resource
        if is_dataclass(nr):
            try:
                if nr._resource_type != "patient":
                    raise TypeError("The new resource must be the same class")
            except:
                pass
        else:
            raise TypeError("The new resource must be the same class")
        
        # check if any resource is not valid
        if force_invalid_merge == False and (self._is_valid == False or nr._is_valid == False):
            raise ValueError("Can't merge invalid resource")
        elif force_invalid_merge == True and (self._is_valid == False or nr._is_valid == False): 
            logging.warning("Merging invalid resources")

        # start merge process
        return replace(self,
                        name = merge_element(self.name, nr.name, mode = "coalesce"),
                        gender = merge_element(self.gender, nr.gender, mode = "coalesce"),
                        birth_date = merge_element(self.birth_date, nr.birth_date, mode = "coalesce"),
                        birth_country = merge_element(self.birth_country, nr.birth_country, mode = "coalesce"),
                        cns = merge_element(self.cns, nr.cns, mode = "coalesce"),
                        active = merge_element(self.active, nr.active, mode = "replace"),
                        address = merge_element(self.address, nr.address, mode = "union", unique_check=True, unique_key="postalCode"),
                        birth_city = merge_element(self.birth_city, nr.birth_city, mode = "coalesce"),
                        deceased = merge_element(self.deceased, nr.deceased, mode = "coalesce"),
                        nationality = merge_element(self.nationality, nr.nationality, mode = "coalesce"),
                        naturalization = merge_element(self.naturalization, nr.naturalization, mode = "coalesce"),
                        mother = merge_element(self.mother, nr.mother, mode = "coalesce"),
                        father = merge_element(self.father, nr.father, mode = "coalesce"),
                        protected_person = merge_element(self.protected_person, nr.protected_person, mode = "coalesce"),
                        race = merge_element(self.race, nr.race, mode = "coalesce"),
                        ethnicity = merge_element(self.ethnicity, nr.ethnicity, mode = "coalesce"),
                        telecom = merge_element(self.telecom, nr.telecom, mode = "union", unique_check=True, unique_key="value"),
                        source = "smsrio",
                        )

    def to_fhir(self):

        # BUILD MORE COMPLEX STRUCTURES
        # Identifier
        identifier = []

        cpf = {"use": "official",
               "type": {
                   "coding": [{
                       "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                       "code": "TAX"}]},
               "system": "https://rnds-fhir.saude.gov.br/NamingSystem/cpf",
               "value": self.cpf}
        identifier.append(cpf)

        if self.cns != "":
            cns = {"use": "official",
                   "type": {
                       "coding": [{
                           "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                           "code": "HC"}]},
                   "system": "https://rnds-fhir.saude.gov.br/NamingSystem/cns",
                   "value": self.cns}
            identifier.append(cns)

        # Name
        name = {"use": "official",
                "text": self.name}

        # Extensions
        extension = []

        # register quality
        if self.register_quality != "":
            registerQuality = {"url":"http://www.saude.gov.br/fhir/r4/StructureDefinition/BRQualidadeCadastroIndividuo-1.0",
                               "valuePositiveInt": self.register_quality}
            extension.append(registerQuality)
        
        # mother
        if self.mother != "":
            mother = {"url": "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRParentesIndividuo-1.0",
                      "extension": [{"url": "relationship",
                                     "valueCode": "mother"},
                                    {"url": "parent",
                                     "valueHumanName": {
                                         "use": "official",
                                         "text": self.mother}}]}
            extension.append(mother)

        # father
        if self.father != "":
            father = {"url": "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRParentesIndividuo-1.0",
                      "extension": [{"url": "relationship",
                                     "valueCode": "father"},
                                    {"url": "parent",
                                     "valueHumanName": {
                                          "use": "official",
                                          "text": self.father}}]}
            extension.append(father)
        
        # race and ethnicity
        if self.race != "" or self.ethnicity != "":
            raceEthnicity = {"url": "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRRacaCorEtnia-1.0",
                             "extension": []}
            
            if self.race != "":
                raceEthnicity["extension"].append({"url": "race",
                                                   "valueCodeableConcept": {
                                                        "coding": [{
                                                            "system": "http://www.saude.gov.br/fhir/r4/CodeSystem/BRRacaCor-1.0",
                                                            "code": self.race }]}})
                
            if self.ethnicity != "":
                raceEthnicity["extension"].append({"url": "indigenousEthnicity",
                                                   "valueCodeableConcept": {
                                                        "coding": [{
                                                            "system": "http://www.saude.gov.br/fhir/r4/CodeSystem/BREtniaIndigena-1.0",
                                                            "code": self.ethnicity }]}})

            extension.append(raceEthnicity)
            
        # birth city
        if self.birth_city != "":
            birthCity = {"url":"http://www.saude.gov.br/fhir/r4/StructureDefinition/BRMunicipio-1.0",
                               "valueCodeableConcept": {
                                   "coding": [{
                                       "system": "https://rnds-fhir.saude.gov.br/CodeSystem/BRMunicipio-1.0",
                                       "code": self.birth_city }]}}
            extension.append(birthCity)    

        # birth country
        if self.birth_country != "":
            birthCountry = {"url":"http://www.saude.gov.br/fhir/r4/StructureDefinition/BRPais-1.0",
                            "valueCodeableConcept": {
                                "coding": [{
                                    "system": "https://rnds-fhir.saude.gov.br/CodeSystem/BRPais-1.0",
                                    "code": self.birth_country }]}}
            
            extension.append(birthCountry) 

        # nationality
        if self.nationality != "":
            nationality = {"url":"http://www.saude.gov.br/fhir/r4/StructureDefinition/BRNacionalidade",
                           "valueCodeableConcept": {
                               "coding": [{
                                   "system": "https://rnds-fhir.saude.gov.br/CodeSystem/BRNacionalidade",
                                   "code": self.nationality }]}}
            
            extension.append(nationality) 

        # naturalization
        if self.naturalization != "":
            naturalization = {"url":"http://www.saude.gov.br/fhir/r4/StructureDefinition/BRNaturalizacao-1.0",
                              "valueCodeableConcept": {
                                  "coding": [{
                                      "system": "https://rnds-fhir.saude.gov.br/CodeSystem/BRNaturalizacao-1.0",
                                      "code": self.naturalization }]}}
            
            extension.append(naturalization) 
        
        # protected person
        if self.protected_person != "":
            protectedPerson = {"url":"http://www.saude.gov.br/fhir/r4/StructureDefinition/BRIndividuoProtegido-1.0",
                               "valueBoolean": self.protected_person}
            extension.append(protectedPerson)
        
    
        # OUTPUT
        return {"identifier": identifier,
                "active": self.active,
                "name": name,
                "telecom": self.telecom,
                "gender": self.gender,
                "birthDate": self.birth_date,
                "deceasedBoolean": self.deceased,
                "address": self.address,
                "extension": extension}
