import math

def sieve(n):
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = bytearray(len(is_prime[i*i::i]))
    return [i for i in range(2, n+1) if is_prime[i]]

# Deep analysis of why k=4 (p_k=7, p_{k+1}=11) gives minimum margin
# The inequality: lcm(1..10) < 7 * lcm(1..7)
# Let's verify this exactly with integers

from math import gcd

def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_range(n):
    result = 1
    for i in range(2, n+1):
        result = lcm(result, i)
    return result

# Exact verification for small cases
print("=== Exact integer verification for small k ===")
primes_small = [2,3,5,7,11,13,17,19,23,29,31,37]
for k in range(len(primes_small)-1):
    pk = primes_small[k]
    pk1 = primes_small[k+1]
    lhs = lcm_range(pk1-1)
    rhs = pk * lcm_range(pk)
    holds = lhs < rhs
    print(f"k={k+1}: lcm(1..{pk1-1})={lhs} {'<' if holds else '>='} {pk}*lcm(1..{pk})={rhs}, ratio={lhs/rhs:.6f}")

print()

# Key insight: margin = log(p_k) - log(product of prime powers in (p_k, p_{k+1}-1])
# For k=4: p_k=7, p_{k+1}=11, prime powers in (7,10] = {8=2^3, 9=3^2}
# ratio = lcm(1..10)/lcm(1..7) = 8*9 / (previous contributions already counted)
# Actually: lcm increases at prime powers. lcm(1..10)/lcm(1..7):
# At 8=2^3: lcm multiplies by 2 (since 2^2=4 was already counted)
# At 9=3^2: lcm multiplies by 3 (since 3^1=3 was already counted)
# So ratio = 2 * 3 = 6, but p_k = 7, so 6 < 7 barely!

print("=== Deep analysis of k=4 case (p_k=7, p_{k+1}=11) ===")
print(f"Prime powers in (7, 10]: 8=2^3, 9=3^2")
print(f"lcm contribution of 8: factor of 2 (since 4=2^2 already in lcm(1..7))")
print(f"lcm contribution of 9: factor of 3 (since 3=3^1 already in lcm(1..7))")
print(f"Total ratio = 2*3 = 6")
print(f"p_k = 7")
print(f"Margin in log: log(7) - log(6) = {math.log(7) - math.log(6):.6f}")
print()

# Now analyze: what makes margin small?
# margin = log(p_k) - sum of log(p) for prime powers p^a strictly between p_k and p_{k+1}
# where the contribution of p^a is log(p) (increment to log_lcm)
# 
# For large prime gaps, there can be many prime powers between p_k and p_{k+1}
# The question is whether their product can exceed p_k

# Let's look at Cramer's conjecture type gaps and see if the margin trend
# Search for cases where the "excess" prime powers in a gap could be large

print("=== Analysis: prime powers in gaps and their product ===")
primes = sieve(10_000_000)
print(f"Using {len(primes)} primes up to 10M")

# Build prime_power_log
max_n = primes[-1]
prime_power_log = {}
for p in primes:
    pk = p
    while pk <= max_n:
        prime_power_log[pk] = math.log(p)
        pk *= p
        if pk > max_n:
            break

# For each gap, compute sum of log(p) for prime powers strictly between p_k and p_{k+1}-1
# margin = log(p_k) - that sum
violations = []
min_margin = float('inf')
min_case = None
small_margins = []

for k in range(len(primes)-1):
    pk = primes[k]
    pk1 = primes[k+1]
    
    # Sum log contributions from prime powers in (p_k, p_{k+1}-1]
    gap_sum = sum(prime_power_log[m] for m in range(pk+1, pk1) if m in prime_power_log)
    margin = math.log(pk) - gap_sum
    
    if margin < min_margin:
        min_margin = margin
        min_case = (k+1, pk, pk1, margin, pk1-pk)
    
    if margin < 0.5:
        small_margins.append((margin, k+1, pk, pk1, pk1-pk))
    
    if margin <= 0:
        violations.append((k+1, pk, pk1, margin))

print(f"Checked {len(primes)-1} pairs")
print(f"Violations: {len(violations)}")
print(f"Minimum margin: {min_margin:.8f} at k={min_case[0]}, p_k={min_case[1]}, p_{{k+1}}={min_case[2]}, gap={min_case[4]}")
print(f"\nAll cases with margin < 0.5:")
small_margins.sort()
for m in small_margins:
    # Show the prime powers in the gap
    pk, pk1 = m[2], m[3]
    pps = [(n, int(round(math.exp(prime_power_log[n]))), prime_power_log[n]) 
           for n in range(pk+1, pk1) if n in prime_power_log]
    print(f"  margin={m[0]:.6f}, k={m[1]}, p_k={pk}, p_{{k+1}}={pk1}, gap={m[4]}, prime_powers={[(x[0]) for x in pps]}")

# Is the minimum margin bounded away from 0 as primes grow?
print("\n=== Margin trend for large primes ===")
# Sample every 1000th prime pair in the large range
sample_indices = range(100000, len(primes)-1, 5000)
sample_margins = []
for k in sample_indices:
    pk = primes[k]
    pk1 = primes[k+1]
    gap_sum = sum(prime_power_log[m] for m in range(pk+1, pk1) if m in prime_power_log)
    margin = math.log(pk) - gap_sum
    sample_margins.append((pk, margin))

print("Sample of (p_k, margin) for large primes:")
for pm in sample_margins[:20]:
    print(f"  p_k={pm[0]:8d}, margin={pm[1]:.4f}")

min_sample = min(sample_margins, key=lambda x: x[1])
print(f"Min in sample: p_k={min_sample[0]}, margin={min_sample[1]:.6f}")