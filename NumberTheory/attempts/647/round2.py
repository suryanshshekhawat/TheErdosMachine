import numpy as np

N = 1000000

# Sieve for number of divisors tau(n)
tau = np.zeros(N+1, dtype=np.int32)
for i in range(1, N+1):
 tau[i::i] += 1

# f(m) = m + tau(m)
f = np.arange(N+1, dtype=np.int64) + tau.astype(np.int64)

# Compute running_max[n] = max(f[1], ..., f[n-1]) for each n
# We'll store it as an array
running_max = np.zeros(N+1, dtype=np.int64)
current_max = 0
for n in range(1, N+1):
 running_max[n] = current_max
 if f[n] > current_max:
 current_max = f[n]

print(f'N searched: {N}')

# Check condition: for n > 24, running_max[n] <= n+2
found = []
for n in range(25, N+1):
 if running_max[n] <= n + 2:
 found.append(n)

print(f'Number of n>24 with max_{{m<n}}(m+tau(m)) <= n+2: {len(found)}')
if found:
 print('First few:')
 for n in found[:20]:
 print(f' n={n}, running_max={running_max[n]}, n+2={n+2}')
else:
 print('No such n found.')

# Show gap = running_max[n] - (n+2) for selected values
print('\nGap = running_max[n]-(n+2) for selected n:')
check_ns = list(range(25, 55)) + [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 999999]
for n in check_ns:
 if n <= N:
 g = int(running_max[n]) - (n + 2)
 print(f' n={n}: running_max={running_max[n]}, gap={g}')

# Find minimum gap over n in [25, N]
gaps = (running_max[25:N+1] - (np.arange(25, N+1, dtype=np.int64) + 2))
min_gap = int(gaps.min())
min_n = int(gaps.argmin()) + 25
print(f'\nMinimum gap over n in [25,{N}]: {min_gap} at n={min_n}')
print(f' running_max[{min_n}]={running_max[min_n]}, {min_n}+2={min_n+2}')