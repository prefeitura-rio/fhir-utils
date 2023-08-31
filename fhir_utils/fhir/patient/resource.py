# -*- coding: utf-8 -*-
from fhir_utils.utils import (
    capitalize_each_word,
    keep_alpha_characters,
    keep_numeric_characters,
    remove_wrong_whitespaces, 
    is_valid_cpf, 
    is_valid_date_format)
from fhir_utils.fhir.merge import compare_resources, merge_resource
from dataclasses import dataclass, field, is_dataclass
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
    register_quality : float = ""
    telecom : list = field(default_factory=list)
    _is_valid: bool = True
    _invalid_elements: list = field(default_factory=list)
    _resource_type = "patient"

    def __post_init__(self):
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
        for i in self.address:
            self.address[i]["postalCode"] = keep_numeric_characters(self.address[i]["postalCode"])

    def format_phone(self):
        for i in self.address:
            if self.telecom[i]["system"] == "phone":
                self.telecom[i]["value"] = keep_numeric_characters(self.telecom[i]["value"])


    def check_cpf(self):
        if not is_valid_cpf(self.cpf):
            self._is_valid = False
            self._invalid_elements.append("cpf")
            #raise ValueError("CPF not valid")

    def check_cns(self):
        if len(self.cns) > 0 and len(self.cns) != 15:
            self._is_valid = False
            self._invalid_elements.append("cns")
            #raise ValueError("CNS must have 15 digits")
        
    def check_birth_country(self):
        if self.gender not in ["B", "E", "N"]:
            self._is_valid = False
            self._invalid_elements.append("birth_country")
    
    def check_birth_date(self):
        if not is_valid_date_format(self.birth_date):
            self._is_valid = False
            self._invalid_elements.append("birth_date")
            #raise ValueError("Birth date must be formated like 'YYYY-MM-DD'")
        elif datetime.strptime(self.birth_date, "%Y-%m-%d") > datetime.now():
            self._is_valid = False
            self._invalid_elements.append("birth_date")
            #raise ValueError("So you were born in the future?")
        elif datetime.strptime(self.birth_date, "%Y-%m-%d") < datetime(1900, 1, 1):
            self._is_valid = False
            self._invalid_elements.append("birth_date")
            #raise ValueError("You cant be that old!")
    
    def check_gender(self):
        if self.gender not in ["male", "female", "unknown"]:
            self._is_valid = False
            self._invalid_elements.append("gender")

    def check_address(self):

        keys = ["use", "type", "line", "city", "state", "postalCode"]

        for i in self.address:
            # if all must have keys are present
            if not all(key in self.address[i] for key in keys):
                self._is_valid = False
                self._invalid_elements.append("address")

            # accepted values
            if self.address[i]["use"] not in ["home", "work", "temp", "old", "billing"]:
                self._is_valid = False
                self._invalid_elements.append("address")

            if self.address[i]["type"] not in ["postal", "physical", "both"]:
                self._is_valid = False
                self._invalid_elements.append("address")

            line = self.address[i]["line"]
            if not 4 <= len(line) <= 5 or line[0] not in ["008", "081"]:
                self._is_valid = False
                self._invalid_elements.append("address")

            if len(keep_numeric_characters(self.address[i]["city"])) != 6:
                self._is_valid = False
                self._invalid_elements.append("address")

            if len(keep_numeric_characters(self.address[i]["state"])) != 2:
                self._is_valid = False
                self._invalid_elements.append("address")

            if len(keep_numeric_characters(self.address[i]["postalCode"])) != 8:
                self._is_valid = False
                self._invalid_elements.append("address")

    def check_telecom(self):
        
        keys = ["system", "value", "use"]

        for i in self.telecom:
            # if all must have keys are present
            if not all(key in self.telecom[i] for key in keys):
                self._is_valid = False
                self._invalid_elements.append("telecom")

            # accepted values
            if self.telecom[i]["system"] not in ["phone", "fax", "email", "pager", "url", "sms", "other"]:
                self._is_valid = False
                self._invalid_elements.append("telecom")

            tel_number = keep_alpha_characters(self.telecom[i]["value"])
            if self.telecom[i]["system"] == "phone" and not 12 <= len(tel_number) <=13: # ddi+ddd+phone
                self._is_valid = False
                self._invalid_elements.append("telecom")

            email = self.telecom[i]["value"]
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                self._is_valid = False
                self._invalid_elements.append("telecom")

    def compare(self, new_resource):
        # compare current patient with another one
        if is_dataclass(new_resource):
            if new_resource._resource_type != "patient":
                raise TypeError("The new resource must be the same class")
        else:
            raise TypeError("The new resource must be the same class")

        return compare_resources(self, new_resource)

    def merge(self, new_resource, force_invalid_merge: False):    
        
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
    