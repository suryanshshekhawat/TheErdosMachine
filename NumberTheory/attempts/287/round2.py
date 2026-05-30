from fractions import Fraction

def search_representations(max_denom=200, max_k=9):
 results = []
 # Stack entries: (remaining, min_next, current_tuple)
 stack = [(Fraction(1), 2, ())]
 while stack:
 remaining, min_val, current = stack.pop()
 if remaining == 0:
 results.append(current)
 continue
 if len(current) >= max_k:
 continue
 slots_left = max_k - len(current)
 # Pruning: even taking 1/min_val for all remaining slots might not be enough
 if slots_left * Fraction(1, min_val) < remaining:
 continue
 # n must satisfy 1/n <= remaining => n >= 1/remaining
 start = max(min_val, int(1 / remaining))
 for n in range(start, max_denom + 1):
 frac = Fraction(1, n)
 if frac > remaining:
 # n too small, keep going (start is already >= 1/remaining so this shouldn't happen)
 continue
 new_remaining = remaining - frac
 # Push to stack
 stack.append((new_remaining, n + 1, current + (n,)))
 # Pruning: if frac < remaining / slots_left roughly, deeper terms won't help
 # Actually prune: if (slots_left-1) * Fraction(1, n+1) < new_remaining
 if slots_left - 1 > 0 and (slots_left - 1) * Fraction(1, n + 1) < new_remaining:
 # Even filling remaining slots won't reach 0
 stack.pop()
 return results

print("Searching Egyptian fraction representations of 1 with denominators in [2,200], at most 9 terms...")
reps = search_representations(max_denom=200, max_k=9)
print(f"Found {len(reps)} representations")

reps_with_gaps = []
for rep in reps:
 if len(rep) < 2:
 continue
 gaps = [rep[i+1] - rep[i] for i in range(len(rep)-1)]
 max_gap = max(gaps)
 reps_with_gaps.append((max_gap, rep, gaps))

reps_with_gaps.sort()

counterexamples = [(mg, rep, gaps) for mg, rep, gaps in reps_with_gaps if mg < 3]
if counterexamples:
 print(f"\nCOUNTEREXAMPLES FOUND (max_gap < 3):")
 for mg, rep, gaps in counterexamples:
 print(f" max_gap={mg}, rep={rep}, gaps={gaps}")
else:
 print("\nNo counterexamples: all representations have max gap >= 3")

print(f"\nMinimum max-gap observed: {reps_with_gaps[0][0] if reps_with_gaps else 'N/A'}")
print("\nTop 20 representations with smallest max gap:")
for mg, rep, gaps in reps_with_gaps[:20]:
 print(f" max_gap={mg}, rep={rep}, gaps={gaps}")