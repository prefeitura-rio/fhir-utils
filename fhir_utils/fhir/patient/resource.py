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
    address : list = field(default_factory=list)
    birth_city : str = ""
    deceased : bool = True
    nationality : str = ""
    naturalization : str = ""
    mother : str = ""
    father : str = ""
    protected_person : bool = ""
    race: str = ""
    ethnicity : str = ""
    telecom : list = field(default_factory=list)
    register_quality : float = field(init = False)
    _is_valid: bool = field(init = False)
    _invalid_elements: list = field(init = False)
    _resource_type : str = field(init = False)

    def __post_init__(self):
        # default values
        self._resource_type = "patient"
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
            for i in self.address:
                try:
                    self.address[i]["postalCode"] = keep_numeric_characters(self.address[i]["postalCode"])
                except:
                    pass

    def format_phone(self):
        if type(self.telecom) is list:
            for i in self.address:
                if self.telecom[i]["system"] == "phone":
                    self.telecom[i]["value"] = keep_numeric_characters(self.telecom[i]["value"])

    def check_cpf(self):
        if not is_valid_cpf(self.cpf):
            self._is_valid = False
            self._invalid_elements.append("cpf")

    def check_cns(self):
        if len(self.cns) > 0 and len(self.cns) != 15:
            self._is_valid = False
            self._invalid_elements.append("cns")
        
    def check_birth_country(self):
        if self.birth_country not in ["B", "E", "N"]:
            self._is_valid = False
            self._invalid_elements.append("birth_country")
    
    def check_birth_date(self):
        if not is_valid_date_format(self.birth_date):
            self._is_valid = False
            self._invalid_elements.append("birth_date")
        elif datetime.strptime(self.birth_date, "%Y-%m-%d") > datetime.now():
            self._is_valid = False
            self._invalid_elements.append("birth_date")
        elif datetime.strptime(self.birth_date, "%Y-%m-%d") < datetime(1900, 1, 1):
            self._is_valid = False
            self._invalid_elements.append("birth_date")
    
    def check_gender(self):
        if self.gender not in ["male", "female", "unknown"]:
            self._is_valid = False
            self._invalid_elements.append("gender")

    def check_address(self):
        if type(self.address) is list:
            keys = ["use", "type", "line", "city", "state", "postalCode"]

            for i in self.address:
                # if all must have keys are present
                if not all(key in self.address[i] for key in keys):
                    self._is_valid = False
                    self._invalid_elements.append("address")

                # accepted values
                elif self.address[i]["use"] not in ["home", "work", "temp", "old", "billing"]:
                    self._is_valid = False
                    self._invalid_elements.append("address")

                elif self.address[i]["type"] not in ["postal", "physical", "both"]:
                    self._is_valid = False
                    self._invalid_elements.append("address")

                elif not 4 <= len(self.address[i]["line"]) <= 5 or self.address[i]["line"][0] not in ["008", "081"]:
                    self._is_valid = False
                    self._invalid_elements.append("address")

                elif len(keep_numeric_characters(self.address[i]["city"])) != 6:
                    self._is_valid = False
                    self._invalid_elements.append("address")

                elif len(keep_numeric_characters(self.address[i]["state"])) != 2:
                    self._is_valid = False
                    self._invalid_elements.append("address")

                elif len(keep_numeric_characters(self.address[i]["postalCode"])) != 8:
                    self._is_valid = False
                    self._invalid_elements.append("address")

    def check_telecom(self):
        
        if type(self.telecom) is list:
            keys = ["system", "value", "use"]

            for i in self.telecom:
                # if all must have keys are present
                if not all(key in self.telecom[i] for key in keys):
                    self._is_valid = False
                    self._invalid_elements.append("telecom")

                # accepted values
                elif self.telecom[i]["system"] not in ["phone", "fax", "email", "pager", "url", "sms", "other"]:
                    self._is_valid = False
                    self._invalid_elements.append("telecom")

                elif self.telecom[i]["system"] == "phone" and not 12 <= len(keep_alpha_characters(self.telecom[i]["value"])) <=13: # ddi+ddd+phone
                    self._is_valid = False
                    self._invalid_elements.append("telecom")

                elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.telecom[i]["value"]):
                    self._is_valid = False
                    self._invalid_elements.append("telecom")

    def calculate_register_quality(self):
        counter = 0

        quality_properties = ["cpf", "gender", "birth_date", "birth_country", "cns",
                               "active", "address", "birth_city", "deceased", "nationality", 
                               "naturalization", "mother", "father", "protected_person", 
                               "race", "ethnicity","telecom"]

        for p in self.__dict__.items():
            if p[0] in quality_properties:
                if type(p[0]) is str and p[1] != "" and p[0] not in self._invalid_elements:
                    counter += 1
                elif type(p[0]) is list and len(p[1]) > 0 and p[0] not in self._invalid_elements:
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
        # TODO: check if new telecom and address are the same or not before appending
        # TODO: mode that discard invalid values

        # check if both resource are of the same type
        if is_dataclass(new_resource):
            try:
                if new_resource._resource_type != "patient":
                    raise TypeError("The new resource must be the same class")
            except:
                pass
        else:
            raise TypeError("The new resource must be the same class")
        
        # check if any resource is not valid
        if force_invalid_merge == False and (self._is_valid == False or new_resource._is_valid == False):
            raise ValueError("Can't merge invalid resource")
            
        if force_invalid_merge == True:
            logging.warning("Force merge invalid resources enabled")

        # start merge process
        return replace(self,
                        name = merge_element(self.name, new_resource.name, mode = "coalesce"),
                        gender = merge_element(self.gender, new_resource.gender, mode = "coalesce"),
                        birth_date = merge_element(self.birth_date, new_resource.birth_date, mode = "coalesce"),
                        birth_country = merge_element(self.birth_country, new_resource.birth_country, mode = "coalesce"),
                        cns = merge_element(self.cns, new_resource.cns, mode = "coalesce"),
                        active = merge_element(self.active, new_resource.active, mode = "replace"),
                        address = merge_element(self.address, new_resource.address, mode = "append"),
                        birth_city = merge_element(self.birth_city, new_resource.birth_city, mode = "coalesce"),
                        deceased = merge_element(self.deceased, new_resource.deceased, mode = "coalesce"),
                        nationality = merge_element(self.nationality, new_resource.nationality, mode = "coalesce"),
                        naturalization = merge_element(self.naturalization, new_resource.naturalization, mode = "coalesce"),
                        mother = merge_element(self.mother, new_resource.mother, mode = "coalesce"),
                        father = merge_element(self.father, new_resource.father, mode = "coalesce"),
                        protected_person = merge_element(self.protected_person, new_resource.protected_person, mode = "coalesce"),
                        race = merge_element(self.race, new_resource.race, mode = "coalesce"),
                        ethnicity = merge_element(self.ethnicity, new_resource.ethnicity, mode = "coalesce"),
                        telecom = merge_element(self.telecom, new_resource.telecom, mode = "append"),
                        source = "smsrio",
                        )
