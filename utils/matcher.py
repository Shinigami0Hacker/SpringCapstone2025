import json
from tinydb import Query
from itertools import combinations

import re
__all__= [
    'validate_schema', 'validate_json_file', 'get_dynamic_variable'
]
def validate_schema(data):
    valid_kinds = {"in", "number", "string"}
    required_fields = {"kind", "name", "pronuciations"}
    optional_fields = {"description", "predefined"}
    allowed_fields = required_fields.union(optional_fields)

    errors = []

    if not isinstance(data, list):
        return False, ["Root should be a list"]

    for index, item in enumerate(data):
        prefix = f"Entry {index + 1}: "

        if not isinstance(item, dict):
            errors.append(f"{prefix}Each item must be a dictionary.")
            continue

        keys = set(item.keys())

        for field in required_fields:
            if field not in item:
                errors.append(f"{prefix}Missing required field '{field}'")

        for field in keys:
            if field not in allowed_fields:
                errors.append(f"{prefix}Unexpected field '{field}' found")

        kind = item.get("kind")
        if kind and kind not in valid_kinds:
            errors.append(f"{prefix}Invalid kind '{kind}', must be one of {valid_kinds}")

        pron = item.get("pronuciations")
        if not isinstance(pron, list):
            errors.append(f"{prefix}'pronuciations' must be a list")

        predefined = item.get("predefined")

        if predefined is not None and kind != "in":
            errors.append(f"{prefix}'predefined' only avaiable in kind 'IN'")
        if predefined is not None and not isinstance(predefined, (str, list)):
            errors.append(f"{prefix}'predefined' must be a string or a list")

    return len(errors) == 0, errors

async def validate_json_file(file_bytes):
    try:
        data = json.loads(file_bytes.decode('utf-8'))
        return data, []
    except json.JSONDecodeError as e:
        return False, f"Invalid json: {e.lineno}:{e.colno}: SyntaxError: {e.msg}"
    except Exception as e:
        return False, f"Error: RuntimeError: {str(e)}"
    
Schema = Query()

def get_dynamic_variable(schema):
    pattern = r"@session\('([^']+)'\)"
    results = []
    for i, entry in enumerate(schema):
        if entry["kind"] == "in":
            matching = re.search(pattern, entry["predefined"])
            if matching:
                variable_name = matching.group(1)
                results.append((variable_name, i))
    if results:
        return (True, results)
    else:
        return (False, None)
    
def ordered_column_permutation(columns):
    """
    Only match when column are spoken in order
    @Output:
    - list[Tuple[Tuple[match_word, index]]]
    """
    result = []
    indexed_lst = list(enumerate(columns))
    for r in range(1, len(columns)+1):
        for comb in combinations(indexed_lst, r):
            values = [value for idx, value in comb]
            indexes = [idx for idx, value in comb]
            result.append((values, indexes))

    return result

