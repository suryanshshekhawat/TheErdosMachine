import math

def sieve(limit):
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = bytearray(len(is_prime[i*i::i]))
    return is_prime

def factorint_simple(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def is_primitive_root(a, p, phi_factors):
    phi = p - 1
    for q_factor in phi_factors:
        if pow(a, phi // q_factor, p) == 1:
            return False
    return True

def smallest_prime_primitive_root(p, is_prime_arr, phi_factors):
    q = 2
    while q < p:
        if is_prime_arr[q]:
            if is_primitive_root(q, p, phi_factors):
                return q
        q += 1
    return None

limit = 10_000_000
print(f"Building sieve up to {limit}...")
is_prime = sieve(limit)

# Get primes; skip p=2 (trivial, only element is 1)
primes = [i for i in range(3, limit+1) if is_prime[i]]

failures = []
# Track top q values (absolute) and notable cases
top_q = []  # (q, p)
max_q = 0
max_q_p = None

print(f"Checking {len(primes)} primes up to {limit}...")

for idx, p in enumerate(primes):
    phi = p - 1
    phi_factors = list(factorint_simple(phi).keys())
    q = smallest_prime_primitive_root(p, is_prime, phi_factors)
    if q is None:
        failures.append(p)
        print(f"FAILURE: p={p}")
    else:
        if q > max_q:
            max_q = q
            max_q_p = p
            top_q.append((q, p))

    if (idx+1) % 100000 == 0:
        print(f"  Progress: {idx+1}/{len(primes)}, failures: {len(failures)}, max_q so far: {max_q} at p={max_q_p}")

print(f"\nTotal primes checked: {len(primes)}")
print(f"Failures: {failures}")
print(f"Largest smallest-prime-prim-root: q={max_q} at p={max_q_p}")
print(f"\nRecord-setters for largest q (in order found):")
for q, p in top_q[-30:]:
    print(f"  p={p}, q={q}, ratio={q/p:.6f}")

# Also show distribution of q values
from collections import Counter
# Recount: histogram of smallest prime primitive root values up to 1M
limit2 = 1_000_000
primes2 = [i for i in range(3, limit2+1) if is_prime[i]]
q_counts = Counter()
for p in primes2:
    phi = p - 1
    phi_factors = list(factorint_simple(phi).keys())
    q = smallest_prime_primitive_root(p, is_prime, phi_factors)
    q_counts[q] += 1

print(f"\nDistribution of smallest prime primitive root (up to p=1M):")
for q in sorted(q_counts.keys()):
    print(f"  q={q}: {q_counts[q]} primes")