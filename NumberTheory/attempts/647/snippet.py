N = 2000000

# Sieve for tau(n)
tau = [0] * (N + 1)
i = 1
while i <= N:
    j = i
    while j <= N:
        tau[j] += 1
        j += i
    i += 1

# f[m] = m + tau[m]
# running_max[n] = max(f[1..n-1]), compute on the fly
# Track minimum gap and where it occurs
print('N searched:', N)

# Check n=24 first
f24 = 24 + tau[24]
rm_at_24 = max(m + tau[m] for m in range(1, 24))
print('n=24: running_max=%d, n+2=%d, gap=%d' % (rm_at_24, 26, rm_at_24-26))
print('f(24)=24+tau(24)=%d+%d=%d' % (24, tau[24], f24))

# Now compute running max and track minimum gap for n>24
cur = max(m + tau[m] for m in range(1, 25))  # max f[1..24]

min_gap = 10**18
min_gap_n = -1
gap_le2_count = 0
gap_le1_count = 0
gap_le0_count = 0

# Also track gaps at powers of 10
checkpoints = {100,1000,10000,100000,1000000,2000000}
checkpoint_gaps = {}

for n in range(25, N + 1):
    rm = cur
    g = rm - (n + 2)
    if g < min_gap:
        min_gap = g
        min_gap_n = n
    if g <= 2:
        gap_le2_count += 1
    if g <= 1:
        gap_le1_count += 1
    if g <= 0:
        gap_le0_count += 1
    if n in checkpoints:
        checkpoint_gaps[n] = (rm, g)
    fn = n + tau[n]
    if fn > cur:
        cur = fn

print('\nMinimum gap in [25,%d]: %d at n=%d' % (N, min_gap, min_gap_n))
print('running_max[%d]=%d, %d+2=%d' % (min_gap_n, min_gap+min_gap_n+2, min_gap_n, min_gap_n+2))
print('Count gap<=2:', gap_le2_count)
print('Count gap<=1:', gap_le1_count)
print('Count gap<=0 (condition met):', gap_le0_count)

print('\nGap at checkpoints:')
for cp in sorted(checkpoint_gaps):
    rm, g = checkpoint_gaps[cp]
    print('  n=%d: running_max=%d, gap=%d' % (cp, rm, g))

# Find all n where gap <= 3 to see the trend
print('\nAll n in [25,%d] with gap<=2:' % N)
cur2 = max(m + tau[m] for m in range(1, 25))
small_gap_ns = []
for n in range(25, N + 1):
    rm = cur2
    g = rm - (n + 2)
    if g <= 2:
        small_gap_ns.append((n, rm, g))
    fn = n + tau[n]
    if fn > cur2:
        cur2 = fn

print('Total with gap<=2:', len(small_gap_ns))
for item in small_gap_ns[:50]:
    print('  n=%d rm=%d gap=%d' % item)