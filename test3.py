# import unicodedata
# import itertools

# # 1. Tone‐mark removal (segmental vs. tonal processing) :contentReference[oaicite:10]{index=10}


# def remove_tone(s: str) -> str:
#     """Strip all combining marks (tones + diacritics) → pure base letters."""
#     nfd = unicodedata.normalize("NFD", s)
#     stripped = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
#     return unicodedata.normalize("NFC", stripped)


# # 2. Phonological substitution map
# import itertools

# SUBSTITUTIONS = {
#     "ngh": ["ng", "g"],
#     "ng":  ["n", "g"],
#     "gi":  ["d"],
#     "qu":  ["q", "k"],
#     "ph":  ["f", "p"],
#     "th":  ["t"],
#     "tr":  ["ch", "t", "c"],

#     "kh":  ["k"],
#     "ch":  ["c"],
#     "y": ["i"],
#     "i": ["y"],
#     "s": ["v"],
#     "t": ["v", "k", "h"],
#     # Final clusters
#     "nh": ["n"],
#     # Vowel-cluster confusions
#     "oa": ["a"]
# }

# def remove_tone(word: str) -> str:
#     # Dummy tone remover: you need a real one for Vietnamese tones
#     return word  # You can replace this with your real tone removal

# def generate_variants(word: str, max_subs: int = 1) -> set[str]:
#     base = remove_tone(word.lower())
#     variants = {base}

#     # Normal substitution variants
#     for n in range(1, max_subs + 1):
#         for combo in itertools.combinations_with_replacement(SUBSTITUTIONS.items(), n):
#             if all(key in base for key, _ in combo):
#                 for choices in itertools.product(*(alts for _, alts in combo)):
#                     tmp = base
#                     for (key, _), alt in zip(combo, choices):
#                         tmp = tmp.replace(key, alt)
#                     variants.add(tmp)

#     # Add prefix-removal variants
#     for prefix in SUBSTITUTIONS.keys():
#         if base.startswith(prefix):
#             new_variant = base[len(prefix):]
#             if new_variant:
#                 variants.add(new_variant)

#     # Add suffix-removal variants
#     for suffix in SUBSTITUTIONS.keys():
#         if base.endswith(suffix):
#             new_variant = base[:-len(suffix)]
#             if new_variant:
#                 variants.add(new_variant)

#     return variants


# if __name__ == "__main__":
#     samples = ["Loại", "Số", "Ký", "Tên"]
#     for w in samples:
#         vs = sorted(generate_variants(w, max_subs=1))
#         print(f"{w} → {vs}")


# # from itertools import product

# # def pair_n_lists_with_space(*lists):
# #     return [' '.join(items) for items in product(*lists)]


# # list1 = ['ten', 'tenn', 'value']
# # list2 = ['thinh', 'hoan', 'thanh']
# # list3 = ['a', 'b']

# # result = pair_n_lists_with_space(list1, list2, list3)

# # for r in result:
# #     print(r)


import re

# Define the pattern
EOS = r"(?:hết|[^\s]*et)\.?$"

# Compile the pattern for efficiency
pattern = re.compile(EOS, re.IGNORECASE)

# List of test cases
test_cases = [
    "hết",       # should match
    "het",       # should match
    "hech",      # should not match
    "vet.",      # should match
    "tet",       # should match
    "abet",      # should match
    "hết.",      # should match
    "street",    # should match
    "set",       # should match
    "hello",     # should not match
    "et",        # should match
    "viet",      # should match
]

# Run the test
print("Matching results:")
for word in test_cases:
    if pattern.search(word):
        print(f"✓ '{word}' matches")
    else:
        print(f"✗ '{word}' does not match")
