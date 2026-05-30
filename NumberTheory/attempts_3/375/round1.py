from sympy import isprime, factorint
import numpy as np

def get_prime_factors(n):
    """Return set of prime factors of n."""
    return set(factorint(n).keys())

def find_composite_gaps(limit, min_gap=2):
    """Find maximal composite gaps up to limit."""
    gaps = []
    n = 1
    while n < limit:
        # Find start of composite run
        while n < limit and isprime(n):
            n += 1
        if n >= limit:
            break
        start = n
        while n < limit and not isprime(n):
            n += 1
        end = n - 1
        gap_len = end - start + 1
        if gap_len >= min_gap:
            gaps.append((start - 1, gap_len))  # n such that n+1,...,n+k are composite
    return gaps

def has_sdr(sets):
    """
    Check if a system of distinct representatives exists using bipartite matching.
    sets: list of sets (each element is the set of primes dividing n+i)
    Returns True if SDR exists.
    """
    k = len(sets)
    if k == 0:
        return True
    
    # Collect all primes
    all_primes = set()
    for s in sets:
        all_primes.update(s)
    prime_list = list(all_primes)
    prime_idx = {p: i for i, p in enumerate(prime_list)}
    m = len(prime_list)
    
    # Bipartite matching: left nodes = indices 0..k-1, right nodes = primes
    # Using augmenting path algorithm
    match_left = [-1] * k   # match_left[i] = prime index matched to left node i
    match_right = [-1] * m  # match_right[j] = left node matched to right node j
    
    def try_augment(u, visited):
        for p in sets[u]:
            j = prime_idx[p]
            if not visited[j]:
                visited[j] = True
                if match_right[j] == -1 or try_augment(match_right[j], visited):
                    match_left[u] = j
                    match_right[j] = u
                    return True
        return False
    
    matched = 0
    for u in range(k):
        visited = [False] * m
        if try_augment(u, visited):
            matched += 1
    
    return matched == k

# Test on composite gaps up to 10^5
print("Searching for composite gaps up to 10^5...")
limit = 100000
gaps = find_composite_gaps(limit, min_gap=1)

print(f"Found {len(gaps)} composite gaps (length >= 1)")

failures = []
max_k_tested = 0

for (n, k) in gaps:
    # Build sets of prime factors for n+1, ..., n+k
    sets = [get_prime_factors(n + i) for i in range(1, k + 1)]
    
    if k > max_k_tested:
        max_k_tested = k
    
    if not has_sdr(sets):
        failures.append((n, k, [n+i for i in range(1, k+1)]))
        print(f"FAILURE: n={n}, k={k}, numbers={[n+i for i in range(1, k+1)]}")

print(f"\nMax gap length tested: {max_k_tested}")
print(f"Total gaps tested: {len(gaps)}")
print(f"Failures found: {len(failures)}")

if not failures:
    print("No counterexamples found up to 10^5. Conjecture holds in this range.")