import tinydb
from utils.normalize import strip_accents
import Levenshtein
import numpy as np

schema_id = "c60e4630-7717-429a-83a3-f119037009c0"

schema_db = tinydb.TinyDB("./database/schema_db.json")
Schema = tinydb.Query()

searched_schema = schema_db.search(Schema.id == schema_id)[0]['schema_content']

transcript = "Tên thạch tiến thuận loại B số ký năm năm hai hết"

# def generate_pattern():
    

# def create_variants(schema):
# 	variants = ()
# 	for entry in schema:
# 		for pronunication in entry['pronuciations']:
			
# 	return (
            
# 	)

 

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



def auto_correct(v, predefined_list):
    dist = []
    for w in predefined_list:
		dis = Levenshtein.distance(v, w)
        dist.append(dis)
	return np.argmax(dist)


def normalize(transcription):
    transcription = transcription.lower()
    transcription = transcription.strip()
    transcription = transcription.rstrip(".")
    return transcription

# def ordered_column_permutation(columns):
#     """
#     Only match when column are spoken in order
#     @Output:
#     - list[Tuple[Tuple[match_word, index]]]
#     """
#     result = []
#     indexed_lst = list(enumerate(columns))
#     for r in range(1, len(columns)+1):
#         for comb in combinations(indexed_lst, r):
#             values = [value for idx, value in comb]
#             indexes = [idx for idx, value in comb]
#             result.append((values, indexes))

#     return result

# TONE_MARKS = {
# 	"\u0300": "huyền",
# 	"\u0301": "sắc",
# 	"\u0303": "ngã",
# 	"\u0309": "hỏi",
# 	"\u0323": "nặng",
# }

# ONSETS = [
# 	"ngh", "ng", "gh", "kh", "ph", "th", "tr", "ch", "qu", "gi",
# 	"b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "q",
# 	"r", "s", "t", "v", "x", ""
# ]
# CODAS = [
# 	"ch", "nh", "ng",
# 	"c", "m", "n", "p", "t",
# 	""
# ]

# def strip_accents(s: str) -> str:
# 	"""Remove *all* combining marks (tone + quality) → pure ASCII letters."""
# 	return "".join(
#     	ch for ch in unicodedata.normalize("NFD", s)
#     	if unicodedata.category(ch) != "Mn"
# 	)

# def extract_tone(s: str):
# 	"""
# 	Decompose to NFD, pull out any tone mark,
# 	return (base_without_tone, tone_name).
# 	"""
# 	nfd = unicodedata.normalize("NFD", s)
# 	tone = "ngang"
# 	kept = []
# 	for ch in nfd:
#         if ch in TONE_MARKS:
#         	tone = TONE_MARKS[ch]
#     	else:
#         	kept.append(ch)
# 	# re‐compose without tone marks
# 	base = unicodedata.normalize("NFC", "".join(kept))
# 	return base, tone

# def decompose_syllable(syllable: str):
# 	"""
# 	Given e.g. "trắng", returns:
#   	{'onset':'tr', 'nucleus':'ang', 'coda':'', 'tone':'sắc'}
# 	All segments are lower-cased and accent-stripped.
# 	"""
# 	raw = syllable.strip().lower()
# 	core, tone = extract_tone(raw)
# 	ascii_core = strip_accents(core)

# 	onset = ""
# 	rem = ascii_core
# 	for o in sorted(ONSETS, key=len, reverse=True):
#     	if ascii_core.startswith(o):
#         	onset = o
#         	rem = ascii_core[len(o):]
#         	break

#     coda = ""
# 	nucleus = rem
# 	for c in sorted(CODAS, key=len, reverse=True):
#     	if rem.endswith(c):
#         	coda = c
#         	nucleus = rem[: len(rem) - len(c)]
#         	break

# 	return {
#     	"onset": onset,
#     	"nucleus": nucleus,
#     	"coda": coda,
#     	"tone": tone
# 	}

str1 = "v"
str2 = "bê"
distance = Levenshtein.distance(str1, str2)
print(f"Levenshtein distance between '{str1}' and '{str2}' is {distance}")