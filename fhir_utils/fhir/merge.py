from deepdiff import DeepDiff
from dataclasses import asdict, replace

def compare_resources(old_resource, new_resource):
    return DeepDiff(asdict(old_resource), asdict(new_resource))

def merge_resource(old_resource):
    return replace(old_resource, name = "thiago")

def merge_element(old_element, new_element, mode = "coalesce", coalesce_priority = "new"):
    match mode:
        case "replace":
            return new_element
        case "union":
            return [old_element, new_element]
        case "coalesce":
            if coalesce_priority == "new":
                return new_element if new_element != "" else old_element
            elif coalesce_priority == "old":
                return old_element if old_element != "" else new_element
            else:
                raise ValueError("Wrong value for coalesce priority")