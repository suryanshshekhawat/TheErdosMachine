import sympy

def tau(n):
    return sympy.divisor_count(n)

# For each n > 24, check if max_{m < n}(m + tau(m)) <= n + 2
# Equivalently, track running max of m + tau(m), and for each n check condition

N = 10000

# Precompute tau for all numbers up to N
tau_vals = [0] * (N + 1)
for i in range(1, N + 1):
    tau_vals[i] = sympy.divisor_count(i)

# Compute m + tau(m) for m from 1 to N
f = [m + tau_vals[m] for m in range(N + 1)]  # f[0] unused

# For each n > 24, check if max(f[1..n-1]) <= n + 2
running_max = 0
candidates = []

for n in range(1, N + 1):
    # Before processing n, running_max = max(f[1..n-1])
    if n > 24:
        if running_max <= n + 2:
            candidates.append((n, running_max, n + 2))
    # Update running max with f[n]
    if f[n] > running_max:
        running_max = f[n]

print(f"Checked n from 25 to {N}")
print(f"Number of candidates found: {len(candidates)}")
if candidates:
    print("First few candidates (n, max_m<n(m+tau(m)), n+2):")
    for c in candidates[:20]:
        print(c)
else:
    print("No candidates found in this range.")

# Also print the running max vs n+2 for n around 25
print("\nn, running_max_before_n, n+2, difference:")
running_max = 0
for n in range(1, 60):
    if n > 1:
        print(f"n={n}, max_before={running_max}, n+2={n+2}, diff={running_max - (n+2)}")
    if f[n] > running_max:
        running_max = f[n]