from fractions import Fraction

def search_representations(max_denom=100, max_k=8):
 results = []
 
 def backtrack(remaining, min_val, current):
 if remaining == 0:
 results.append(tuple(current))
 return
 if len(current) >= max_k:
 return
 # Pruning: even if we take 1/min_val for remaining slots, can we reach 0?
 slots_left = max_k - len(current)
 if slots_left * Fraction(1, min_val) < remaining:
 return
 # Pruning: next fraction must be <= remaining
 max_next = int(1 / remaining) + 1
 start = max(min_val, max_next)
 
 for n in range(start, max_denom + 1):
 frac = Fraction(1, n)
 if frac > remaining:
 break
 backtrack(remaining - frac, n + 1, current + [n])
 
 backtrack(Fraction(1), 2, [])
 return results

print("Searching Egyptian fraction representations of 1...")
reps = search_representations(max_denom=200, max_k=9)
print(f"Found {len(reps)} representations")

min_max_gap = None
best_rep = None
counterexamples = []

for rep in reps:
 if len(rep) < 2:
 continue
 gaps = [rep[i+1] - rep[i] for i in range(len(rep)-1)]
 max_gap = max(gaps)
 if min_max_gap is None or max_gap < min_max_gap:
 min_max_gap = max_gap
 best_rep = rep
 if max_gap < 3:
 counterexamples.append((rep, gaps, max_gap))

print(f"\nMinimum of max-gap across all representations: {min_max_gap}")
print(f"Best (smallest max-gap) representation: {best_rep}")

if counterexamples:
 print(f"\nCOUNTEREXAMPLES FOUND (max_gap < 3):")
 for rep, gaps, mg in counterexamples:
 print(f" {rep}, gaps={gaps}, max_gap={mg}")
else:
 print("\nNo counterexamples found: all representations have max gap >= 3")

# Also print a few reps with smallest max gaps
reps_with_gaps = []
for rep in reps:
 if len(rep) < 2:
 continue
 gaps = [rep[i+1] - rep[i] for i in range(len(rep)-1)]
 max_gap = max(gaps)
 reps_with_gaps.append((max_gap, rep, gaps))

reps_with_gaps.sort()
print("\nTop 20 representations with smallest max gap:")
for mg, rep, gaps in reps_with_gaps[:20]:
 print(f" max_gap={mg}, rep={rep}, gaps={gaps}")