from dataclasses import dataclass
from fhir_utils.fhir.merge import compare_resources, merge_element

@dataclass
class Resource:
    id: int
    name: str

def test_compare_resources():
    old_resource = Resource(1, "old")
    new_resource = Resource(1, "new")

    assert compare_resources(old_resource, new_resource) == {"values_changed": {"root.name": {"new_value": "new", "old_value": "old"}}}

def test_merge_element_replace():
    old_element = "old"
    new_element = "new"

    merged = merge_element(old_element, new_element, mode="replace")
    assert merged == "new"

def test_merge_element_union():
    old_element = ["old"]
    new_element = ["new"]
    merged = merge_element(old_element, new_element, mode="union", unique_check= False)
    assert merged == ["old", "new"]

    old_element = [{"key": "a", "value": 1}, {"key": "b", "value": 2}]
    new_element = [{"key": "c", "value": 3}, {"key": "b", "value": 2}]
    merged = merge_element(old_element, new_element, mode="union", unique_check= True, unique_key="key")
    assert merged ==  [{"key": "a", "value": 1}, {"key": "b", "value": 2}, {"key": "c", "value": 3}]


def test_merge_element_coalesce():
    old_element = "old"
    new_element = ""

    merged = merge_element(old_element, new_element, mode="coalesce")
    assert merged == "old"