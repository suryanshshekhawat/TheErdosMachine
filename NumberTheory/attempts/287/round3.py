from fractions import Fraction

results = []
stack = [(Fraction(1), 2, ())]
max_denom = 200
max_k = 9

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
    start = max(min_val, int(1 / remaining))
    for n in range(start, max_denom + 1):
        frac = Fraction(1, n)
        if frac > remaining:
            continue
        new_remaining = remaining - frac
        new_current = current + (n,)
        if slots_left - 1 > 0:
            if (slots_left - 1) * Fraction(1, n + 1) < new_remaining:
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

print('Top 20 representations with smallest max gap:')
for mg, rep, gaps in reps_with_gaps[:20]:
    print('  max_gap=%d rep=%s gaps=%s' % (mg, rep, gaps))