from deepdiff import DeepDiff
from dataclasses import replace, is_dataclass

def compare_resources(old_resource, new_resource):
    """
    Compare two resources and return the differences.

    Args:
        old_resource (object): The original resource to compare.
        new_resource (object): The new resource to compare.

    Returns:
        dict: A dictionary containing the differences between the two resources.
    """
    if is_dataclass(old_resource) and is_dataclass(new_resource):
        return DeepDiff(old_resource, new_resource)
    else:
        raise TypeError("Resource must be a dataclass or an instance of one")

def merge_element(old_element, new_element, mode = "coalesce", coalesce_priority = "old", unique_check = False, unique_key ="" ):
    """
    Merge two elements based on the specified mode.
    
    Args:
        old_element (any): The original element to be merged.
        new_element (any): The new element to merge with the original.
        mode (str, optional): The merging mode. Defaults to "coalesce".
            Possible values: "replace", "union", "coalesce".
        coalesce_priority (str, optional): The priority for coalesce mode.
            Defaults to "old". Possible values: "old", "new".
        unique_check (bool, optional): Flag to indicate whether to perform unique check in union mode. Defaults to False.
        unique_key (str, optional): The key to use for unique check in union mode. Defaults to "".
    
    Returns:
        any: The merged element based on the specified mode.
    """
    match mode:
        case "replace":
            return new_element
        case "union":
            if unique_check == False:
                return sum([old_element, new_element],[]) # flatten nested list
            elif unique_check == True:
                flat_list = sum([old_element, new_element],[])
                unique_list = []
                unique_keys = []
                for e in flat_list:
                    if type(e) is dict:
                        if not e[unique_key] in unique_keys:
                            unique_keys.append(e[unique_key])
                            unique_list.append(e)
                    else:
                        raise TypeError("Old and New element both must be a list of dictionaries")
                return unique_list     
            else:
                raise ValueError("Unique_check value must be boolean")      
        case "coalesce":
            if coalesce_priority == "old":
                return old_element if old_element != "" else new_element
            elif coalesce_priority == "new":
                return new_element if new_element != "" else old_element
            else:
                raise ValueError("Wrong value for coalesce priority")
            