import math

def sieve(n):
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = bytearray(len(is_prime[i*i::i]))
    return [i for i in range(2, n+1) if is_prime[i]]

# Extend search to 2,000,000
limit = 2_000_000
primes = sieve(limit)
print(f"Generated {len(primes)} primes up to {limit}")

max_needed = primes[-1]  # last prime

# Build prime_power_log: n -> log(p) if n=p^a
prime_power_log = {}
for p in primes:
    pk = p
    while pk <= max_needed:
        prime_power_log[pk] = math.log(p)
        pk *= p
        if pk > max_needed:
            break

# Sweep and record log_lcm at p_k and p_{k+1}-1
# We need values at all p_k and p_{k+1}-1
needed = set()
for k in range(len(primes)-1):
    needed.add(primes[k])
    needed.add(primes[k+1] - 1)

log_lcm_vals = {}
lcm_val = 0.0
for n in range(1, max_needed + 1):
    if n in prime_power_log:
        lcm_val += prime_power_log[n]
    if n in needed:
        log_lcm_vals[n] = lcm_val

print(f"Computed log_lcm at needed points")

# Check inequality and track minimum margin
violations = []
min_margin = float('inf')
min_case = None

# Also track cases where margin < 1 (potentially dangerous)
small_margin_cases = []

for k in range(len(primes)-1):
    pk = primes[k]
    pk1 = primes[k+1]
    
    lhs = log_lcm_vals[pk1 - 1]
    rhs = math.log(pk) + log_lcm_vals[pk]
    diff = rhs - lhs
    
    if diff < min_margin:
        min_margin = diff
        min_case = (k+1, pk, pk1, diff)
    
    if diff < 0.5:
        small_margin_cases.append((k+1, pk, pk1, diff))
    
    if lhs >= rhs:
        violations.append((k+1, pk, pk1, lhs, rhs, diff))

print(f"Checked k=1 to k={len(primes)-1}")
print(f"Largest prime checked: p_k = {primes[-2]}, p_{{k+1}} = {primes[-1]}")
print(f"Total violations found: {len(violations)}")

if violations:
    print("VIOLATIONS:")
    for v in violations:
        print(f"  k={v[0]}, p_k={v[1]}, p_{{k+1}}={v[2]}, diff={v[5]:.8f}")

print(f"\nMinimum margin (rhs-lhs): {min_margin:.8f}")
print(f"  at k={min_case[0]}, p_k={min_case[1]}, p_{{k+1}}={min_case[2]}")

print(f"\nCases with margin < 0.5 (potentially close calls):")
for c in small_margin_cases[:30]:
    print(f"  k={c[0]}, p_k={c[1]}, p_{{k+1}}={c[2]}, margin={c[3]:.8f}")

# Theoretical analysis: the inequality is equivalent to
# log(lcm(p_k..p_{k+1}-1) / lcm(1..p_k)) < log(p_k)  ... wait
# Actually: lcm(1..p_{k+1}-1) / lcm(1..p_k) = product of prime powers p^a with p_k < p^a <= p_{k+1}-1
# Since p_{k+1} is the next prime after p_k, the only prime powers in (p_k, p_{k+1}-1]
# are prime powers of primes LESS than p_k (since p_k < p^a < p_{k+1} means p < p_{k+1})
# So inequality becomes: product of prime powers p^a in (p_k, p_{k+1}-1] < p_k

print("\n--- Theoretical structure ---")
print("The ratio lcm(1..p_{k+1}-1)/lcm(1..p_k) = product of prime powers strictly between p_k and p_{k+1}-1")
print("Margin = log(p_k) - log(ratio)")
print("\nCases with small margin tend to occur when prime gaps are large")

# Show the 20 smallest margins and the prime gaps
print("\n20 smallest margin cases:")
all_margins = []
for k in range(len(primes)-1):
    pk = primes[k]
    pk1 = primes[k+1]
    lhs = log_lcm_vals[pk1 - 1]
    rhs = math.log(pk) + log_lcm_vals[pk]
    diff = rhs - lhs
    all_margins.append((diff, k+1, pk, pk1, pk1-pk))

all_margins.sort()
for m in all_margins[:20]:
    print(f"  margin={m[0]:.6f}, k={m[1]}, p_k={m[2]}, p_{{k+1}}={m[3]}, gap={m[4]}")