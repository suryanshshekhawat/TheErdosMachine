# Pure stdlib + numpy only

def sieve(limit):
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    i = 2
    while i * i <= limit:
        if is_prime[i]:
            is_prime[i*i::i] = bytearray(len(range(i*i, limit+1, i)))
        i += 1
    return is_prime

def prime_factors(n, small_primes):
    factors = set()
    temp = n
    for p in small_primes:
        if p * p > temp:
            break
        if temp % p == 0:
            factors.add(p)
            while temp % p == 0:
                temp //= p
    if temp > 1:
        factors.add(temp)
    return factors

def has_sdr(sets):
    k = len(sets)
    if k == 0:
        return True
    all_primes = set()
    for s in sets:
        all_primes.update(s)
    prime_list = list(all_primes)
    prime_idx = {p: i for i, p in enumerate(prime_list)}
    m = len(prime_list)
    match_right = [-1] * m

    def try_aug(u, visited):
        for p in sets[u]:
            j = prime_idx[p]
            if not visited[j]:
                visited[j] = True
                if match_right[j] == -1 or try_aug(match_right[j], visited):
                    match_right[j] = u
                    return True
        return False

    matched = 0
    for u in range(k):
        vis = [False] * m
        if try_aug(u, vis):
            matched += 1
    return matched == k

LIMIT = 200000
is_prime = sieve(LIMIT + 10)
small_primes = [i for i in range(2, 1000) if is_prime[i]]

failures = []
max_k = 0
total_gaps = 0

n = 2
while n < LIMIT:
    while n < LIMIT and is_prime[n]:
        n += 1
    if n >= LIMIT:
        break
    start_c = n
    while n < LIMIT and not is_prime[n]:
        n += 1
    end_c = n - 1
    n_prob = start_c - 1
    k = end_c - start_c + 1
    total_gaps += 1
    if k > max_k:
        max_k = k
    sets = [prime_factors(n_prob + i, small_primes) for i in range(1, k + 1)]
    if not has_sdr(sets):
        info = [(n_prob + i, sorted(sets[i-1])) for i in range(1, k+1)]
        failures.append((n_prob, k, info))
        print("FAILURE: n={}, k={}".format(n_prob, k))
        for ni, fs in info:
            print("  {}: primes={}".format(ni, fs))

print("Limit={}, total_gaps={}, max_gap_k={}".format(LIMIT, total_gaps, max_k))
print("Failures: {}".format(len(failures)))
if not failures:
    print("No counterexamples found. Conjecture holds in this range.")