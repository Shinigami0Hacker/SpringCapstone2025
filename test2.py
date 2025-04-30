import tinydb
from utils.normalize import strip_accents
import Levenshtein
import numpy as np
import unicodedata
import re
import itertools

"if not match end of tokens, all cases will fail"

schema_id = "35cb8076-1b0d-47d9-bcd3-7340b25f8fec"

schema_db = tinydb.TinyDB("./database/schema_db.json")
Schema = tinydb.Query()

content = schema_db.search(Schema.id == schema_id)[0]['schema_content']
nums_column = len(content)

transcript = "băng một chiều dài e chiều rộng xê số ký năm sáu một hết."
transcript1 = "Hoan thi thu thao loại B so ky hello năm hai hết"
transcript2 = "Ten thạch tiến thuận loại B số ki hello năm hai hết"

EOS = r"(?:hết|hech|chet|[^\s]*et)\.?$"

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

def auto_correct(v, predefined_list):
    dist = []
    for w in predefined_list:
        n = len(w)
        dis = Levenshtein.distance(v[:n], w)
        dist.append(dis)
    return predefined_list[np.argmin(dist)]

DYNAMIC_VAR = [
     ['Thạch Tiến Thịnh', 'Nguyễn Hùng Vinh', ' Lê Ngọc Khánh'],
     [],
     []
]


def strip_accents(s: str) -> str:
	"""Remove *all* combining marks (tone + quality) → pure ASCII letters."""
	return "".join(
    	ch for ch in unicodedata.normalize("NFD", s)
    	if unicodedata.category(ch) != "Mn"
	)

def normalize(transcription):
    transcription = transcription.lower()
    transcription = transcription.strip()
    transcription = transcription.rstrip(".")
    return transcription


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

def ordered_column_permutation(columns):
    """
    Only match when column are spoken in order
    @Output:
    - list[Tuple[Tuple[match_word, index]]]
    """
    result = []
    indexed_lst = list(enumerate(columns))
    for r in range(1, len(columns)+1):
        for comb in itertools.combinations(indexed_lst, r):
            values = [value for idx, value in comb]
            indexes = [idx for idx, value in comb]
            result.append((values, indexes))
    return result

def formatation_service(entries, indicies):
    entries = entries[:]
    for i in indicies:
        if entries[i] != None:
            if content[i]['kind'] == "number":
                entries[i] = number_convertor(entries[i])
            if content[i]['kind'] == "in":
                predefined = content[i]['predefined']
                if isinstance(predefined, str):
                    entries[i] = auto_correct(entries[i], DYNAMIC_VAR[i]).title()
                if isinstance(predefined, list):
                    predefined = list(map(lambda x: x.lower(), predefined))
                    entries[i] = auto_correct(entries[i], predefined).title()
    return entries


def create_pronunciation_variants(pronunciations):
    result = []
    for pronunciation in pronunciations:
        # pronunciation = pronunciation.lower()
        # pronunciation_removed_tone = strip_accents()
        # pronunciation_removed_tone.append(pronunciation)
        # result.append(pattern)
        pass
    return result

def strip_accents(s: str) -> str:
	"""Remove *all* combining marks (tone + quality) → pure ASCII letters."""
	return "".join(
    	ch for ch in unicodedata.normalize("NFD", s)
    	if unicodedata.category(ch) != "Mn"
	)


def create_matching_token():
    pass
"""
Orginal-matching -> matching-variants -> matching permutation -> mapping -> auto-correct
[
    [patten, ()]
]
"""


def remove_tone(s: str) -> str:
    """Strip all combining marks (tones + diacritics) → pure base letters."""
    nfd = unicodedata.normalize("NFD", s)
    stripped = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", stripped)

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


from itertools import product


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
            print(pattern)
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
            return result, indices
    return None, None

def pairing(*lists):
    return [' '.join(items) for items in product(*lists)]

def pipe(transcript):
    transcript = normalize(transcript)
    final_result = [None] * nums_column
    transcript_no_tone = strip_accents(transcript)
    pronunciations = list(map(lambda x: x['pronuciations'], content))
    print(pronunciations)
    res = matching(transcript, pronunciations)
    if res:
        final_result = formatation_service(res, list(range(nums_column)))
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
            final_result = formatation_service(variant_result, list(range(nums_column)))
            return final_result
    # Handle permutation, first to orginal
    per_res, indicies = handle_permuatation_logic(transcription=transcript_no_tone, pronunciations=variants_pronunciations, reference_sentence=transcript)
    if per_res:
        final_result = formatation_service(entries=per_res, indicies=indicies)
        return final_result
    return final_result
print(pipe(transcript=transcript))

# def create_variants(schema):
# 	variants = []
# 	for entry in schema:
# 		for pronunication in entry['pronuciations']:
#             print(pronunication)
#     return 1

# def matching_pipeline():
#     idx = []
#     for data in idx:
        



from itertools import combinations





# print(ordered_column_permutation([1, 2, 3]))

# def extract_tone(s: str):
#     """
#     Decompose to NFD, pull out any tone mark,
#     return (base_without_tone, tone_name).
#     """
#     nfd = unicodedata.normalize("NFD", s)
#     tone = "ngang"
#     kept = []
#     for ch in nfd:
#         if ch in TONE_MARKS:
#             tone = TONE_MARKS[ch]
#         else:
#             kept.append(ch)
#     # re‐compose without tone marks
#     base = unicodedata.normalize("NFC", "".join(kept))
#     return base, tone

# def decompose_syllable(syllable: str):
#     """
#     Given e.g. "trắng", returns:
#     {'onset':'tr', 'nucleus':'ang', 'coda':'', 'tone':'sắc'}
#     All segments are lower-cased and accent-stripped.
#     """
#     raw = syllable.strip().lower()
#     core, tone = extract_tone(raw)
#     ascii_core = strip_accents(core)

#     onset = ""
#     rem = ascii_core
#     for o in sorted(ONSETS, key=len, reverse=True):
#         if ascii_core.startswith(o):
#             onset = o
#             rem = ascii_core[len(o):]
#             break

#     coda = ""
#     nucleus = rem
#     for c in sorted(CODAS, key=len, reverse=True):
#         if rem.endswith(c):
#             coda = c
#             nucleus = rem[: len(rem) - len(c)]
#             break

#     return {
#         "onset": onset,
#         "nucleus": nucleus,
#         "coda": coda,
#         "tone": tone
#     }
# str1 = ["Khanh", "Huy", "Vinh"]
# str2 = "Khang"
# distance = []
# for s1 in str1:
#     distance.append(Levenshtein.distance(s1, str2))
# print(str1[np.argmin(distance)])