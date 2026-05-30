from fractions import Fraction
from collections import Counter

def find_egyptian_representations(max_denom=40):
    """
    Find all representations of 1 as sum of distinct unit fractions
    with denominators in [2, max_denom].
    """
    results = []
    
    def backtrack(remaining, start, current):
        if remaining == 0:
            results.append(tuple(current))
            return
        for d in range(start, max_denom + 1):
            f = Fraction(1, d)
            if f > remaining:
                break
            # Pruning: even if we take all remaining fractions, can we reach remaining?
            # Upper bound on remaining sum: 1/d + 1/(d+1) + ... (geometric-ish)
            # Simple prune: if 1/d < remaining and no further terms can help, skip
            # Just proceed with simple recursion + fraction comparison
            backtrack(remaining - f, d + 1, current + (d,))
    
    backtrack(Fraction(1), 2, ())
    return results

print("Searching Egyptian fraction representations of 1 (denominators 2..40)...")
results = find_egyptian_representations(max_denom=40)
print(f"Total representations found: {len(results)}")
print()

# Analyze gaps
gap_dist = Counter()
min_max_gap = None
best_rep = None
counterexamples = []

for rep in results:
    if len(rep) < 2:
        continue
    gaps = [rep[i+1] - rep[i] for i in range(len(rep)-1)]
    mg = max(gaps)
    gap_dist[mg] += 1
    if min_max_gap is None or mg < min_max_gap:
        min_max_gap = mg
        best_rep = (rep, gaps)
    if mg < 3:
        counterexamples.append((rep, gaps, mg))

print(f"Distribution of max consecutive gaps:")
for k in sorted(gap_dist):
    print(f"  max_gap={k}: {gap_dist[k]} representations")

print()
print(f"Minimum max-gap found: {min_max_gap}")
print(f"Best (smallest max-gap) representation: {best_rep[0]}")
print(f"Gaps: {best_rep[1]}")

print()
if counterexamples:
    print(f"COUNTEREXAMPLES FOUND (max_gap < 3):")
    for ce in counterexamples:
        print(f"  {ce[0]}, gaps={ce[1]}, max_gap={ce[2]}")
        # Verify sum
        s = sum(Fraction(1, d) for d in ce[0])
        print(f"  Verification: sum = {s}")
else:
    print("No counterexamples found (all representations have max_gap >= 3).")

# Also show a few representations with smallest max gap
print()
print("Top 5 representations with smallest max-gap:")
sorted_reps = sorted(
    [(rep, [rep[i+1]-rep[i] for i in range(len(rep)-1)]) for rep in results if len(rep) >= 2],
    key=lambda x: max(x[1])
)
for rep, gaps in sorted_reps[:5]:
    print(f"  {rep}, gaps={gaps}, max_gap={max(gaps)}")