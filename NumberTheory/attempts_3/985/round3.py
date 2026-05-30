import math

def sieve(limit):
    """Sieve of Eratosthenes."""
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

limit = 1_000_000
print(f"Building sieve up to {limit}...")
is_prime = sieve(limit)
primes = [i for i in range(3, limit+1) if is_prime[i]]

failures = []
worst_cases = []
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
        ratio = q / p
        if ratio > 0.3:
            worst_cases.append((p, q, ratio))

    if (idx+1) % 10000 == 0:
        print(f"  Progress: {idx+1}/{len(primes)}, failures so far: {len(failures)}")

print(f"\nTotal primes checked: {len(primes)}")
print(f"Failures: {failures}")
print(f"Largest absolute q found: q={max_q} at p={max_q_p}")
print(f"Cases where ratio q/p > 0.3: {len(worst_cases)}")
print(f"Top 20 worst ratios:")
for p, q, r in sorted(worst_cases, key=lambda x: -x[2])[:20]:
    print(f"  p={p}, q={q}, ratio={r:.4f}")