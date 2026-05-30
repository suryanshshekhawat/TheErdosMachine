from fractions import Fraction
from itertools import combinations

def find_egyptian_fraction_representations(target, min_denom, max_denom, max_terms):
    """
    Find all representations of target as sum of distinct unit fractions
    with denominators in [min_denom, max_denom].
    Returns list of tuples of denominators (sorted).
    """
    results = []
    
    def backtrack(remaining, start, current):
        if remaining == 0:
            results.append(tuple(current))
            return
        if not current and remaining > Fraction(1, start):
            # Need at least one term <= remaining
            pass
        
        for d in range(start, max_denom + 1):
            f = Fraction(1, d)
            if f > remaining:
                break
            # Check if remaining terms can sum to remaining - f
            # Upper bound: sum of 1/d + 1/(d+1) + ... 
            # If f == remaining - f... just try
            backtrack(remaining - f, d + 1, current + [d])
    
    backtrack(target, min_denom, max_denom)
    return results

# Search for representations of 1 with distinct denominators > 1
# where all consecutive gaps are <= 2
# Start with small max_denom

print("Searching for Egyptian fraction representations of 1...")
print("Looking for cases where ALL consecutive gaps are <= 2")
print("(i.e., max gap < 3, which would be a counterexample)")
print()

# Try with denominators up to 50, varying number of terms
all_counterexamples = []

for max_d in [20, 30, 40, 50]:
    results = find_egyptian_fraction_representations(Fraction(1), 2, max_d, 20)
    
    for rep in results:
        if len(rep) < 2:
            continue
        gaps = [rep[i+1] - rep[i] for i in range(len(rep)-1)]
        max_gap = max(gaps)
        if max_gap < 3:
            all_counterexamples.append((rep, gaps, max_gap))
            print(f"POTENTIAL COUNTEREXAMPLE: {rep}")
            print(f"  Gaps: {gaps}, Max gap: {max_gap}")

if not all_counterexamples:
    print("No counterexamples found in searched range.")
    print()
    # Show statistics on what we found
    results = find_egyptian_fraction_representations(Fraction(1), 2, 30, 20)
    print(f"Total representations found with max denom <= 30: {len(results)}")
    
    min_max_gap = None
    best_rep = None
    for rep in results:
        if len(rep) < 2:
            continue
        gaps = [rep[i+1] - rep[i] for i in range(len(rep)-1)]
        max_gap = max(gaps)
        if min_max_gap is None or max_gap < min_max_gap:
            min_max_gap = max_gap
            best_rep = (rep, gaps)
    
    print(f"Minimum max-gap found: {min_max_gap}")
    print(f"Best representation: {best_rep[0]}")
    print(f"Gaps: {best_rep[1]}")
    
    # Show distribution of max gaps
    from collections import Counter
    gap_dist = Counter()
    for rep in results:
        if len(rep) >= 2:
            gaps = [rep[i+1] - rep[i] for i in range(len(rep)-1)]
            gap_dist[max(gaps)] += 1
    print(f"\nDistribution of max gaps: {dict(sorted(gap_dist.items()))}")