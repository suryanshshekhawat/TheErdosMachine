# Implement tau (divisor count) without sympy using a sieve
def compute_tau_sieve(N):
    tau = [0] * (N + 1)
    for i in range(1, N + 1):
        for j in range(i, N + 1, i):
            tau[j] += 1
    return tau

N = 100000

tau_vals = compute_tau_sieve(N)

# f[m] = m + tau(m)
# For each n > 24, check if max(f[1], ..., f[n-1]) <= n + 2

running_max = 0
candidates = []

for n in range(1, N + 1):
    # running_max = max(f[1..n-1]) at this point
    if n > 24:
        fn2 = n + 2
        if running_max <= fn2:
            candidates.append((n, running_max, fn2))
    # Update running max with f[n] = n + tau[n]
    val = n + tau_vals[n]
    if val > running_max:
        running_max = val

print(f"Checked n from 25 to {N}")
print(f"Number of candidates found: {len(candidates)}")
if candidates:
    print("Candidates (n, max_m<n(m+tau(m)), n+2):")
    for c in candidates[:30]:
        print(c)
else:
    print("No candidates found in this range.")

# Print some diagnostics: how fast does running_max grow vs n+2?
print("\nSample of running_max vs n+2 (every 1000 steps):")
running_max = 0
for n in range(1, N + 1):
    if n > 24 and n % 1000 == 0:
        print(f"n={n}, running_max={running_max}, n+2={n+2}, excess={running_max-(n+2)}")
    val = n + tau_vals[n]
    if val > running_max:
        running_max = val

# Also check small values near n=24 carefully
print("\nDetailed view n=20 to 50:")
running_max2 = 0
for n in range(1, 51):
    if n > 1:
        status = "CANDIDATE" if (n > 24 and running_max2 <= n+2) else ""
        print(f"n={n}, max_before={running_max2}, n+2={n+2}, excess={running_max2-(n+2)} {status}")
    val = n + tau_vals[n]
    if val > running_max2:
        running_max2 = val