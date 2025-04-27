import unicodedata

def strip_accents(s: str) -> str:
	"""Remove *all* combining marks (tone + quality) → pure ASCII letters."""
	return "".join(
    	ch for ch in unicodedata.normalize("NFD", s)
    	if unicodedata.category(ch) != "Mn"
	)