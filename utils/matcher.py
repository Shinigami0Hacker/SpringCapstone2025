import json
from tinydb import Query
from itertools import combinations
from utils.normalize import strip_accents
import Levenshtein
import numpy as np
import unicodedata
import re
import itertools

__all__= [
    'validate_schema', 'validate_json_file', 'get_dynamic_variable'
]

EOS = r"(?:hết|het|hech|vet|tet)\.?$"

ANY_PATTERN = r"\s+(.+?)\s+"

PERMUATION_PATTERN = [
    [],
    [],
    [],
    []
]

TONE_MARKS = {
	"\u0300": "huyền",
	"\u0301": "sắc",
	"\u0303": "ngã",
	"\u0309": "hỏi",
	"\u0323": "nặng",
}

ONSETS = [
	"ngh", "ng", "gh", "kh", "ph", "th", "tr", "ch", "qu", "gi",
	"b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "q",
	"r", "s", "t", "v", "x", ""
]
CODAS = [
	"ch", "nh", "ng",
	"c", "m", "n", "p", "t",
	""
]

SUBSTITUTIONS = {
    "ngh": ["ng", "g"],
    "ng":  ["n", "g"],
    "gi":  ["d"],
    "qu":  ["q", "k"],
    "ph":  ["f", "p"],
    "th":  ["t"],
    "tr":  ["ch", "t", "c"],
    "kh":  ["k"],
    "ch":  ["c"],
    "y": ["i"],
    "i": ["y"],
    "v": ["s"],
    "t": ["v", "k"],
    # Final clusters
    "nh": ["n"],
    "ch": ["c"],
    "ng": ["n", "g"],
    # Vowel‐cluster confusions
    "oa": ["a"],
    "nh": ["n"]
}


def normalize(transcription):
    transcription = transcription.lower()
    transcription = transcription.strip()
    transcription = transcription.rstrip(".")
    return transcription


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

def remove_tone(s: str) -> str:
    """Strip all combining marks (tones + diacritics) → pure base letters."""
    nfd = unicodedata.normalize("NFD", s)
    stripped = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", stripped)

# -------------------

def generate_variants(word: str, max_subs: int = 2) -> set[str]:
    base = remove_tone(word.lower())
    variants = {base}

    for n in range(1, max_subs + 1):
        for combo in itertools.combinations_with_replacement(SUBSTITUTIONS.items(), n):
            if all(key in base for key, _ in combo):
                for choices in itertools.product(*(alts for _, alts in combo)):
                    tmp = base
                    for (key, _), alt in zip(combo, choices):
                        tmp = tmp.replace(key, alt)
                    variants.add(tmp)
    return list(variants)
# -------------------

def create_matching_token_pattern(pronunciations):
	tmp = "(?:"
	for i in range(len(pronunciations)):
		word = pronunciations[i]
		if any(c.isspace() for c in word):	
			tmp2 = list(map(lambda x: f"(?:{x})", word.split(" ")))
			tmp2 = "\s+".join(tmp2)
			tmp2 = "(?:" + tmp2 + ")"
			tmp += tmp2 + "|"
		else:
			tmp += word + "|"
	else:
		tmp = tmp.rstrip("|")
	return tmp + ")"

def number_convertor(string_numbers):
    number_map = {
        "không": 0,
        "một":1,
        "hai":2,
        "ba":3,
        "bốn":4,
        "năm":5,
        "sáu":6,
        "bảy":7,
        "tám":8,
        "chín":9,
        "xấu": 6,
        "chấm": ".",
        "phẩy": ","
    }
    second_layer_mapping = {
         strip_accents(k)
          : v for k, v in number_map.items()
    }
    result = ""
    unmatch_words = []
    for i, string_number in enumerate(string_numbers.split()):
        converted_number = number_map.get(string_number.strip())
        if converted_number:
            result += str(converted_number)
        else:
             unmatch_words.append((i, string_number))

    if unmatch_words:
        for index, unmatch_words in unmatch_words:
            converted_number_layer2 = second_layer_mapping.get(unmatch_words.strip())
            if converted_number_layer2:
                result = result[:index] + str(converted_number_layer2) + result[index:]
    return result

def generate_pattern(sub_patterns, i):
    """
    Example: r"^tên\s+(.+?)\s+(?:loại|loai|lai|loan)\s+(.+?)\s+số\s+(?:kí|ký|ky|kỹ)\s+(.+?)\s+hết\.?$"
    """
    pattern = ""
    SOT = "(?:\s*.+?)?"
    pattern += SOT
    for x in range(len(sub_patterns)):
            pattern += sub_patterns[x] + ANY_PATTERN
    pattern += EOS
    return pattern

def matching(transcription, pronunciations, reference_sentence = None):
    tokens = []
    for pronunciation in pronunciations:
        pronunciation = list(map(str.lower, pronunciation))
        tokens.append(create_matching_token_pattern(pronunciation))
    pattern = generate_pattern(tokens, list(range(len(pronunciations))))
    nums_column = len(pronunciations)
    m = re.match(pattern, transcription)
    result = []
    if m:
        for i in range(nums_column):
                if not reference_sentence:
                    extracted_word = m.group(i + 1)
                    if extracted_word:
                        result.append(extracted_word)
                else:
                    start = m.start(i + 1)
                    end = m.end(i + 1)
                    result.append(reference_sentence[start:end])
    return result

def auto_correct(v, predefined_list):
    dist = []
    for w in predefined_list:
        if w == 'c' and strip_accents(v) == 'xe':
            return 'C'
        dis = Levenshtein.distance(v, w)
        dist.append(dis)
    return predefined_list[np.argmin(dist)]

def formatation_service(entries, indicies, content, dynamic_var):
    entries = entries[:]
    for i in indicies:
        if entries[i] != None:
            if content[i]['kind'] == "number":
                entries[i] = number_convertor(entries[i])
                continue
            if content[i]['kind'] == "in":
                 predefined = content[i]['predefined']
                 if isinstance(predefined, str):
                    if dynamic_var is not None:
                        entries[i] = auto_correct(entries[i], list(map(lambda x: x.lower(), dynamic_var[i]))).title()
                 if isinstance(predefined, list):
                    predefined = list(map(lambda x: x.lower(), predefined))
                    entries[i] = auto_correct(entries[i], predefined).title()
        entries[i] = entries[i].title()        
    return entries


def pairing(*lists):
    return [' '.join(items) for items in itertools.product(*lists)]

def handle_permuatation_logic(transcription, pronunciations, reference_sentence = None):
    tokens = []
    for pronunciation in pronunciations:
        pronunciation = list(map(str.lower, pronunciation))
        tokens.append(create_matching_token_pattern(pronunciation))
    permuatations = sorted(ordered_column_permutation(tokens), key=lambda x: len(x[1]), reverse=True)
    nums_column = len(pronunciations)
    result = [None] * nums_column
    for permuatation in permuatations:
        pattern = generate_pattern(permuatation[0], permuatation[1])
        m = re.match(pattern, transcription)
        if m:
            indices = permuatation[1]
            for i in range(len(indices)):
                    if not reference_sentence:
                        extracted_word = m.group(i + 1)
                        if extracted_word:
                            result[indices[i]] = extracted_word
                    else:
                        start = m.start(i + 1)
                        end = m.end(i + 1)
                        result[indices[i]] = reference_sentence[start:end]
            if 0 not in indices and 1 in indices:
                start = m.start(1)
                f_value = reference_sentence[:start - len(m.group(1))]
                indices.append(0)
                result[0] = f_value
            return result, sorted(indices)
    return None, None


def pipe(transcript, content, dynamic_var):
    transcript = normalize(transcript)
    nums_column = len(content)
    final_result = [None] * nums_column
    transcript_no_tone = strip_accents(transcript)
    pronunciations = list(map(lambda x: x['pronuciations'], content))
    res = matching(transcript, pronunciations)
    if res:
        final_result = formatation_service(entries=res, indicies=list(range(nums_column)), dynamic_var=dynamic_var, content=content)
        return final_result
    else:
        # Handle variants replication
        variants_pronunciations = [None] * nums_column
        for i in range(nums_column):
            tmp = []
            for word in pronunciations[i]:
                if re.search(r'\s', word):
                    split_words = word.split() 
                    tmp2 = []
                    for v in range(len(split_words)):
                        w = generate_variants(split_words[v])
                        tmp2.append(w)
                    else:
                        words = pairing(*tmp2)
                        tmp.extend(words)
                else:
                    tmp.extend(generate_variants(word))
            variants_pronunciations[i] = tmp
        variant_result =  matching(transcript_no_tone, variants_pronunciations, reference_sentence=transcript)
        if variant_result:
            final_result = formatation_service(entries=variant_result,indicies=list(range(nums_column)), content=content, dynamic_var=dynamic_var)
            return final_result
    # Handle permutation, first to orginal
    per_res, indicies = handle_permuatation_logic(transcription=transcript_no_tone, pronunciations=variants_pronunciations, reference_sentence=transcript)
    if per_res:
        final_result = formatation_service(entries=per_res, indicies=indicies, dynamic_var=dynamic_var, content=content)
        return final_result
    return final_result


