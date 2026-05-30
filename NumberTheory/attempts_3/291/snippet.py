from math import gcd, lcm, isqrt

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0: return False
    return True

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

# Key pattern observed: runs of gcd=1 seem to start at or near prime powers
# Runs start at: 1,9=3^2, 27=3^3, 49=7^2, 125=5^3, 243=3^5, 289=17^2, 361=19^2, 841=29^2, 1369=37^2, 2401=7^4, 3125=5^5, 3721=61^2

prime_power_starts = [1, 9, 27, 49, 125, 243, 289, 361, 841, 968, 1164, 1331, 1369, 2401, 3125, 3488, 3721]
print("Checking if run starts are prime powers:")
for n in prime_power_starts:
    # Check if n is a prime power
    pf = prime_factors(n)
    is_pp = len(pf) == 1
    p = list(pf)[0] if pf else None
    k = 0
    tmp = n
    if p:
        while tmp % p == 0:
            k += 1
            tmp //= p
    print(f"  n={n}: prime_factors={pf}, is_prime_power={is_pp}, {p}^{k}={p**k if p else 'N/A'}")

print()
# Strong pattern: runs of gcd=1 appear to start at prime powers p^k
# and end just before the next prime power or some other threshold

# Let's look at prime powers up to 5000
prime_powers = []
for p in range(2, 5001):
    if is_prime(p):
        pk = p
        while pk <= 5000:
            prime_powers.append(pk)
            pk *= p
prime_powers.sort()
print(f"Prime powers up to 5000 (first 30): {prime_powers[:30]}")

# Now check: does gcd become 1 at each prime power?
def compute_sequence(max_n):
    results = []
    L_prev = 1
    a_prev = 1
    results.append((1, a_prev, L_prev, 1))
    for n in range(2, max_n + 1):
        L_curr = lcm(L_prev, n)
        a_curr = a_prev * (L_curr // L_prev) + L_curr // n
        g = gcd(a_curr, L_curr)
        results.append((n, a_curr, L_curr, g))
        L_prev = L_curr
        a_prev = a_curr
    return results

results = compute_sequence(5000)
gcd_dict = {n: g for n, a, L, g in results}

print("\nGCD at prime powers:")
for pk in prime_powers[:40]:
    if pk <= 5000:
        g = gcd_dict[pk]
        pf = prime_factors(pk)
        p = list(pf)[0]
        print(f"  n={pk} ({p}^k): gcd={g}")

print()
# Hypothesis: p | a_n iff p^2 <= n < next prime power after p^2?
# Let's check Wolstenholme-type: for prime p, when does p | a_n?
# Known: p | a_n for p^2 <= n < p^(k+1) related to Wolstenholme's theorem

# Check: for each prime p, find range where p | gcd
print("\nFor each prime p, ranges where p | gcd(a_n, L_n):")
for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
    p_divides = [n for n in range(1, 5001) if gcd_dict[n] % p == 0]
    if p_divides:
        # Find runs
        runs = []
        s = p_divides[0]
        e = p_divides[0]
        for n in p_divides[1:]:
            if n == e + 1:
                e = n
            else:
                runs.append((s, e))
                s = e = n
        runs.append((s, e))
        print(f"  p={p}: {runs[:8]}")