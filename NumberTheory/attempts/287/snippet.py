from fractions import Fraction
import math

results = []
stack = [(Fraction(1), 2, ())]
max_denom = 150
max_k = 10

while stack:
    remaining, min_val, current = stack.pop()
    if remaining == Fraction(0):
        results.append(current)
        continue
    if len(current) >= max_k:
        continue
    slots_left = max_k - len(current)
    if slots_left * Fraction(1, min_val) < remaining:
        continue
    lo = math.ceil(remaining.denominator / remaining.numerator)
    start = max(min_val, lo)
    hi = min(max_denom, int(slots_left / remaining))
    for n in range(start, hi + 1):
        frac = Fraction(1, n)
        new_remaining = remaining - frac
        new_current = current + (n,)
        sl2 = slots_left - 1
        if sl2 > 0 and new_remaining > Fraction(0):
            if sl2 * Fraction(1, n + 1) < new_remaining:
                continue
        stack.append((new_remaining, n + 1, new_current))

print('Found', len(results), 'representations')

reps_with_gaps = []
for rep in results:
    if len(rep) < 2:
        continue
    gaps = [rep[i+1] - rep[i] for i in range(len(rep)-1)]
    max_gap = max(gaps)
    reps_with_gaps.append((max_gap, rep, gaps))

reps_with_gaps.sort()

counterexamples = [(mg, rep, gaps) for mg, rep, gaps in reps_with_gaps if mg < 3]
if counterexamples:
    print('COUNTEREXAMPLES FOUND (max_gap < 3):')
    for mg, rep, gaps in counterexamples:
        print('  max_gap=%d rep=%s gaps=%s' % (mg, rep, gaps))
else:
    print('No counterexamples: all representations have max gap >= 3')

if reps_with_gaps:
    print('Minimum max-gap observed:', reps_with_gaps[0][0])
    print('Representations achieving min max-gap:')
    min_mg = reps_with_gaps[0][0]
    for mg, rep, gaps in reps_with_gaps:
        if mg == min_mg:
            print('  max_gap=%d rep=%s gaps=%s' % (mg, rep, gaps))
        else:
            break
    print('\nTop 20 with smallest max gap:')
    for mg, rep, gaps in reps_with_gaps[:20]:
        print('  max_gap=%d rep=%s gaps=%s' % (mg, rep, gaps))

# Count by number of terms
from collections import Counter
term_counts = Counter(len(rep) for _, rep, _ in reps_with_gaps)
print('\nRepresentations by number of terms:', sorted(term_counts.items()))