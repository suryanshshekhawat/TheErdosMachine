import sympy
from sympy import isprime, primitive_root, factorint, primerange
import math

def multiplicative_order(a, n):
    """Compute multiplicative order of a mod n."""
    if math.gcd(a, n) != 1:
        return None
    order = 1
    current = a % n
    while current != 1:
        current = (current * a) % n
        order += 1
    return order

def is_primitive_root(a, p):
    """Check if a is a primitive root mod p (p prime)."""
    phi = p - 1
    factors = factorint(phi)
    for q_factor in factors:
        if pow(a, phi // q_factor, p) == 1:
            return False
    return True

def smallest_prime_primitive_root(p):
    """Find smallest prime q that is a primitive root mod p."""
    for q in primerange(2, p):
        if is_primitive_root(q, p):
            return q
    return None

# Check primes up to a modest limit first
limit = 10000
primes = list(primerange(3, limit))  # skip p=2, trivial

failures = []
max_ratio = 0
max_ratio_p = None
worst_cases = []

print(f"Checking primes up to {limit}...")
for p in primes:
    q = smallest_prime_primitive_root(p)
    if q is None:
        failures.append(p)
        print(f"FAILURE: p={p}, no prime primitive root found < p")
    else:
        ratio = q / p
        if ratio > max_ratio:
            max_ratio = ratio
            max_ratio_p = p
        if q > p // 2:  # notable cases where q is large relative to p
            worst_cases.append((p, q, ratio))

print(f"\nTotal primes checked: {len(primes)}")
print(f"Failures (no prime primitive root < p): {failures}")
print(f"Max ratio q/p: {max_ratio:.4f} at p={max_ratio_p}")
print(f"\nWorst cases (q > p/2):")
for p, q, r in sorted(worst_cases, key=lambda x: -x[2])[:20]:
    print(f"  p={p}, smallest prime prim root q={q}, ratio={r:.4f}")