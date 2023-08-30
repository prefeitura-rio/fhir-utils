# -*- coding: utf-8 -*-
from dataclasses import dataclass, field

@dataclass
class Patient:
    source : str
    name : str
    birth_date : str
    cpf : str
    cns : str = ""
    gender : str = "unknow"
    active : bool = True
    address : list = field(default_factory=list)
    birth_city : str = ""
    birth_country : str = "01"
    deceased : bool = True
    nationality : str = ""
    naturalization : str = ""
    mother : str = ""
    father : str = ""
    protected_person : bool = False
    race: str = ""
    ethnicity : str = ""
    register_quality : float = 0
    telecom : list = field(default_factory=list)

    def __post_init__(self):
        self.name = self.name.title()
        # verifica validade da pk

        # verifica presença dos campos obrigatórios

    #def compliance_check

    #def padroniza textos

    #def dicarcad_incomplinat

    #def to_fhir