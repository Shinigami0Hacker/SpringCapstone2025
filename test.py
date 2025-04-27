from itertools import combinations

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

TONE_MARKS = {
	"\u0300": "huyền",  # grave
	"\u0301": "sắc",	# acute
	"\u0303": "ngã",	# tilde
	"\u0309": "hỏi",	# hook
	"\u0323": "nặng",   # dot below
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

def strip_accents(s: str) -> str:
	"""Remove *all* combining marks (tone + quality) → pure ASCII letters."""
	return "".join(
    	ch for ch in unicodedata.normalize("NFD", s)
    	if unicodedata.category(ch) != "Mn"
	)

def extract_tone(s: str):
	"""
	Decompose to NFD, pull out any tone mark,
	return (base_without_tone, tone_name).
	"""
	nfd = unicodedata.normalize("NFD", s)
	tone = "ngang"
	kept = []
	for ch in nfd:
        if ch in TONE_MARKS:
        	tone = TONE_MARKS[ch]
    	else:
        	kept.append(ch)
	# re‐compose without tone marks
	base = unicodedata.normalize("NFC", "".join(kept))
	return base, tone

def decompose_syllable(syllable: str):
	"""
	Given e.g. "trắng", returns:
  	{'onset':'tr', 'nucleus':'ang', 'coda':'', 'tone':'sắc'}
	All segments are lower-cased and accent-stripped.
	"""
	raw = syllable.strip().lower()
	core, tone = extract_tone(raw)
	ascii_core = strip_accents(core)

	onset = ""
	rem = ascii_core
	for o in sorted(ONSETS, key=len, reverse=True):
    	if ascii_core.startswith(o):
        	onset = o
        	rem = ascii_core[len(o):]
        	break

    coda = ""
	nucleus = rem
	for c in sorted(CODAS, key=len, reverse=True):
    	if rem.endswith(c):
        	coda = c
        	nucleus = rem[: len(rem) - len(c)]
        	break

	return {
    	"onset": onset,
    	"nucleus": nucleus,
    	"coda": coda,
    	"tone": tone
	}
