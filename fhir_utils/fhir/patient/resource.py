# -*- coding: utf-8 -*-

class Patient:

    elements_required = ["active", "birthCountry", "birthDate", "gender", "identifier", "name"]

    def __init__(self, patient: dict, source: str):

        #verify
        
        # verify if all required elements are in patient
        elements_required_missing = []
        for key in elements_required:
            if key not in patient:
                elements_required_missing.append(key)
        if len(elements_required_missing) > 0:
                raise f"Missing required element(s): {elements_required_missing}"


        self.source = source
        self.active = None
        self.address =  None
        self.birth_city =  None
        self.birth_country =  None
        self.birth_date =  None
        self.deceased =  None
        self.gender =  None
        self.identifier =  None
        self.name =  None
        self.nationality =  None
        self.naturalization =  None
        self.parents =  None
        self.protected_person =  None
        self.race_ethnicity =  None
        self.register_quality =  None
        self.telecom =  None
        