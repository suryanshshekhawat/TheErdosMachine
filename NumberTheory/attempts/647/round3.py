import numpy as np

N = 1000000

# Sieve for number of divisors tau(n)
tau = np.zeros(N+1, dtype=np.int32)
for i in range(1, N+1):
    tau[i::i] += 1

# f(m) = m + tau(m)
f = np.arange(N+1, dtype=np.int64) + tau.astype(np.int64)

# running_max[n] = max(f[1..n-1])
# Use np.maximum.accumulate on f[1..N], then shift
f_vals = f[1:]  # f[1], f[2], ..., f[N]
cummax = np.maximum.accumulate(f_vals)  # cummax[i] = max(f[1..i+1])
# running_max[n] = max(f[1..n-1]) = cummax[n-2] for n>=2, 0 for n=1
# running_max[n] for n in [1..N]:
running_max = np.zeros(N+1, dtype=np.int64)
running_max[2:] = cummax[:-1]  # running_max[2]=f[1], running_max[3]=max(f[1],f[2]), etc.

print('N searched:', N)

# Check condition for n > 24
n_arr = np.arange(25, N+1, dtype=np.int64)
rm = running_max[25:N+1]
cond = rm <= n_arr + 2
count = int(cond.sum())
print('Number of n>24 with max_{m<n}(m+tau(m)) <= n+2:', count)

if count > 0:
    idxs = np.where(cond)[0]
    print('First few such n:')
    for idx in idxs[:20]:
        n = int(idx) + 25
        print('  n=%d, running_max=%d, n+2=%d' % (n, running_max[n], n+2))
else:
    print('No such n found.')

# Gap analysis
gaps = rm - (n_arr + 2)
min_gap = int(gaps.min())
min_n = int(gaps.argmin()) + 25
print('\nMinimum gap over n in [25,%d]: %d at n=%d' % (N, min_gap, min_n))
print('  running_max[%d]=%d, %d+2=%d' % (min_n, running_max[min_n], min_n, min_n+2))

# Show gap for a range around n=25
print('\nGap for n=25..60:')
for n in range(25, 61):
    g = int(running_max[n]) - (n+2)
    print('  n=%d rm=%d gap=%d' % (n, running_max[n], g))

print('\nGap at large n:')
for n in [1000, 10000, 100000, 500000, 999999]:
    g = int(running_max[n]) - (n+2)
    print('  n=%d rm=%d gap=%d' % (n, running_max[n], g))