from itertools import combinations, permutations

def ordered_column_permutation2(columns):
    """
    Generate all permutations of all combinations of the input columns.
    Output:
        List of tuples (values, indexes) sorted by length of values, descending.
    """
    result = []
    indexed_lst = list(enumerate(columns))
    
    for r in range(1, len(columns) + 1):
        for comb in combinations(indexed_lst, r):
            for perm in permutations(comb):
                values = [value for idx, value in perm]
                indexes = [idx for idx, value in perm]
                result.append((values, indexes))

    return sorted(result, key=lambda x: len(x[0]), reverse=True)

def ordered_column_permutation1(columns):
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
examples = [1, 2, 3]
print("-" * 100)
print(*ordered_column_permutation1(examples), sep="\n")
print("-" * 100)
print(*ordered_column_permutation2(examples), sep="\n")