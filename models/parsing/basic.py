import re

pattern = r"Tên\s([A-Za-zÀ-ÿ\s]+)\sSố ký\s(năm năm)"

def get_config_matrix():
    with open(""):
        pass

def from_schema_to_pattern():
    pattern = r"(Tên\s([A-Za-zÀ-ÿ\s]+)\sSố ký\s(năm năm))|(Số ký\s(năm năm)\sTên\s([A-Za-zÀ-ÿ\s]+))"

def match_group(text, pattern):
    match = re.search(pattern, text)
    if match:
        return match.groups()

