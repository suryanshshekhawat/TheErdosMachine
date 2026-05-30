from fractions import Fraction
from collections import Counter

def find_egyptian_representations(max_denom=30):
    """
    Find all representations of 1 as sum of distinct unit fractions
    with denominators in [2, max_denom].
    """
    results = []
    
    # Precompute suffix sums for pruning
    suffix_sum = {}
    s = Fraction(0)
    for d in range(max_denom, 1, -1):
        s += Fraction(1, d)
        suffix_sum[d] = s
    
    def backtrack(remaining, start, current):
        if remaining == 0:
            results.append(tuple(current))
            return
        if start > max_denom:
            return
        # Pruning: max achievable from start..max_denom
        if suffix_sum.get(start, Fraction(0)) < remaining:
            return
        for d in range(start, max_denom + 1):
            f = Fraction(1, d)
            if f > remaining:
                # fractions are decreasing, so if 1/d > remaining, 
                # wait - we need 1/d <= remaining to be useful
                # Actually if f > remaining skip this d
                continue
            if f == remaining:
                results.append(tuple(current) + (d,))
                # Don't break - no larger d can equal remaining (1/d decreases)
                break
            # Check suffix sum from d+1
            if d + 1 <= max_denom and suffix_sum.get(d+1, Fraction(0)) >= remaining - f:
                backtrack(remaining - f, d + 1, tuple(current) + (d,))
    
    backtrack(Fraction(1), 2, ())
    return results

# First verify with a known small example
# 1 = 1/2 + 1/3 + 1/6
test = Fraction(1,2) + Fraction(1,3) + Fraction(1,6)
print(f"Test: 1/2+1/3+1/6 = {test}")

# Try to find ANY representation first
print("Searching with max_denom=20...")
results = find_egyptian_representations(max_denom=20)
print(f"Found: {len(results)} representations")
for r in results[:10]:
    print(f"  {r}, sum={sum(Fraction(1,d) for d in r)}")