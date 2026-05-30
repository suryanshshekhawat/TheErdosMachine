from math import gcd, log, floor
import math

def sieve(n):
    """Return list of primes up to n using sieve of Eratosthenes."""
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = bytearray(len(is_prime[i*i::i]))
    return [i for i in range(2, n+1) if is_prime[i]]

def log_lcm(n, primes_up_to_n):
    """Compute log(lcm(1,...,n)) using prime factorization."""
    result = 0.0
    for p in primes_up_to_n:
        if p > n:
            break
        # Sum floor(log_p(n)) * log(p) = log(p^floor(log_p(n)))
        pk = p
        while pk <= n:
            result += math.log(p)
            pk *= p
    return result

# Generate primes up to 200000
limit = 200000
primes = sieve(limit)
print(f"Generated {len(primes)} primes up to {limit}")

violations = []
results = []

# Precompute log_lcm incrementally
# log_lcm(n) changes from log_lcm(n-1) only if n is a prime power
# We'll compute for each p_{k+1}-1 and p_k

# Actually compute incrementally:
# log_lcm(m) = log_lcm(m-1) + log(p)*a if m = p^a (prime power), else log_lcm(m-1)

def is_prime_power(n, prime_set):
    """If n is a prime power p^a, return (p, a), else None."""
    if n < 2:
        return None
    for p in [2, 3, 5, 7, 11, 13]:  # small primes first
        if p > n:
            break
        if n % p == 0:
            a = 0
            m = n
            while m % p == 0:
                m //= p
                a += 1
            if m == 1:
                return (p, a)
            return None
    # Check if n itself is prime
    if n in prime_set:
        return (n, 1)
    return None

prime_set = set(primes)

# Build log_lcm array incrementally
# log_lcm_vals[n] = log(lcm(1..n))
max_val = primes[-1]  # up to last prime

# We only need log_lcm at p_k and p_{k+1}-1
# Compute incrementally up to max needed value

log_lcm_current = 0.0
log_lcm_at = {}  # store at needed points

needed = set()
for k in range(len(primes)-1):
    needed.add(primes[k])        # p_k
    needed.add(primes[k+1] - 1)  # p_{k+1} - 1

current_n = 1
log_lcm_current = 0.0

# We need to iterate n from 1 to max(needed)
max_needed = max(needed)

# For efficiency, precompute which n are prime powers
# n is prime power if n = p^a for some prime p, a>=1
prime_power_log = {}  # n -> log contribution
for p in primes:
    pk = p
    while pk <= max_needed:
        prime_power_log[pk] = math.log(p)
        pk *= p
        if pk > max_needed:
            break

# Now sweep
log_lcm_vals = {}
lcm_val = 0.0
for n in range(1, max_needed + 1):
    if n in prime_power_log:
        lcm_val += prime_power_log[n]
    if n in needed:
        log_lcm_vals[n] = lcm_val

print(f"Computed log_lcm at {len(log_lcm_vals)} needed points")

# Now check the inequality
violations = []
min_margin = float('inf')
min_case = None

for k in range(len(primes)-1):
    pk = primes[k]
    pk1 = primes[k+1]
    
    lhs = log_lcm_vals[pk1 - 1]
    rhs = math.log(pk) + log_lcm_vals[pk]
    diff = rhs - lhs
    
    if diff < min_margin:
        min_margin = diff
        min_case = (k+1, pk, pk1, lhs, rhs, diff)
    
    if lhs >= rhs:
        violations.append((k+1, pk, pk1, lhs, rhs, diff))

print(f"Checked k=1 to k={len(primes)-1}")
print(f"Largest prime checked: p_k = {primes[-2]}, p_{{k+1}} = {primes[-1]}")
print(f"Total violations found: {len(violations)}")

if violations:
    print("VIOLATIONS:")
    for v in violations:
        print(f"  k={v[0]}, p_k={v[1]}, p_{{k+1}}={v[2]}, lhs={v[3]:.6f}, rhs={v[4]:.6f}, diff={v[5]:.6f}")
else:
    print("No violations found - inequality holds for all checked cases!")

print(f"\nMinimum margin (rhs-lhs): {min_margin:.8f}")
print(f"  at k={min_case[0]}, p_k={min_case[1]}, p_{{k+1}}={min_case[2]}")

# Show first 15 cases
print("\nFirst 15 cases:")
for k in range(min(15, len(primes)-1)):
    pk = primes[k]
    pk1 = primes[k+1]
    lhs = log_lcm_vals[pk1-1]
    rhs = math.log(pk) + log_lcm_vals[pk]
    print(f"  k={k+1}, p_k={pk:4d}, p_{{k+1}}={pk1:4d}, margin={rhs-lhs:.6f}")