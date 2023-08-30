from deepdiff import DeepDiff
from dataclasses import asdict

def compare_resources(old_resource, new_resource):
 # ref https://www.askpython.com/python/dictionary/compare-two-dictionaries
    return DeepDiff(asdict(old_resource), asdict(new_resource))