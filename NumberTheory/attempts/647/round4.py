N = 200000

# Sieve for tau(n) = number of divisors
tau = [0] * (N + 1)
i = 1
while i <= N:
    j = i
    while j <= N:
        tau[j] += 1
        j += i
    i += 1

# f[m] = m + tau[m]
f = [0] * (N + 1)
for m in range(1, N + 1):
    f[m] = m + tau[m]

# running_max[n] = max(f[1], ..., f[n-1])
# Compute incrementally
running_max = [0] * (N + 1)
cur = 0
for n in range(1, N + 1):
    running_max[n] = cur
    cur = cur if cur >= f[n] else f[n]

print('N searched:', N)

# Check condition for n > 24
found = []
for n in range(25, N + 1):
    rm = running_max[n]
    if rm <= n + 2:
        found.append((n, rm))

print('Count of n>24 satisfying condition:', len(found))
if found:
    print('First 20:')
    for n, rm in found[:20]:
        print('  n=%d running_max=%d n+2=%d' % (n, rm, n+2))
else:
    print('No such n found in [25, %d].' % N)

# Show gaps
print('\nGap = running_max[n]-(n+2) for n=25..55:')
for n in range(25, 56):
    print('  n=%d rm=%d gap=%d' % (n, running_max[n], running_max[n]-(n+2)))

print('\nGap at selected large n:')
for n in [100, 1000, 5000, 10000, 50000, 100000, 199999]:
    g = running_max[n] - (n+2)
    print('  n=%d rm=%d gap=%d' % (n, running_max[n], g))

# Min gap and location
min_gap = None
min_n = None
for n in range(25, N+1):
    g = running_max[n] - (n+2)
    if min_gap is None or g < min_gap:
        min_gap = g
        min_n = n
print('\nMinimum gap: %d at n=%d (running_max=%d, n+2=%d)' % (min_gap, min_n, running_max[min_n], min_n+2))