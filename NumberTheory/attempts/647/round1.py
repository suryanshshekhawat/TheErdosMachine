import numpy as np

N = 1000000

# Compute tau(n) for all n up to N using sieve
tau = np.ones(N+1, dtype=np.int32)
for i in range(2, N+1):
 tau[i::i] += 1
# tau[i] is actually number of divisors: start with 1 and add 1 for each multiple
# Wait, let me redo: tau[n] = number of divisors
# Standard sieve for divisor count
tau2 = np.zeros(N+1, dtype=np.int32)
for i in range(1, N+1):
 tau2[i::i] += 1

# f(m) = m + tau(m)
f = np.arange(N+1, dtype=np.int64) + tau2.astype(np.int64)

# running maximum of f(m) for m < n, i.e., max over m=1..n-1
# running_max[n] = max(f[1], f[2], ..., f[n-1])
running_max = np.zeros(N+1, dtype=np.int64)
running_max[1] = f[1] # max of empty set, set to 0
current_max = 0
for n in range(1, N+1):
 # running_max before processing n is max f[1..n-1]
 # We want for each n: max_{m<n} f(m) <= n+2
 if n > 1:
 running_max[n] = current_max
 else:
 running_max[n] = 0
 if f[n] > current_max:
 current_max = f[n]

# Now check condition: for n > 24, running_max[n] <= n+2
results = []
for n in range(25, N+1):
 if running_max[n] <= n + 2:
 results.append((n, running_max[n], n+2, running_max[n]-(n+2)))

print(f'N searched: {N}')
print(f'Number of n>24 with max_{{m<n}}(m+tau(m)) <= n+2: {len(results)}')
if results:
 print('First few such n:')
 for r in results[:20]:
 print(f' n={r[0]}, running_max={r[1]}, n+2={r[2]}, gap={r[3]}')
else:
 print('No such n found.')

# Show the gap (running_max[n] - (n+2)) for n around 25 and periodically
print('\nGap = running_max[n] - (n+2) for selected n:')
for n in list(range(25, 50)) + list(range(100, 110)) + [1000, 10000, 100000, 500000, 999999]:
 if n <= N:
 g = running_max[n] - (n+2)
 print(f' n={n}: running_max={running_max[n]}, gap={g}')

# Also find minimum gap and where it occurs
gaps = np.array([running_max[n] - (n+2) for n in range(25, N+1)])
min_gap = gaps.min()
min_idx = gaps.argmin() + 25
print(f'\nMinimum gap in range [25,{N}]: {min_gap} at n={min_idx}')
print(f' running_max[{min_idx}]={running_max[min_idx]}, {min_idx}+2={min_idx+2}')