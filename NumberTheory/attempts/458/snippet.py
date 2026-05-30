from sympy import primerange, nextprime
import math

# lcm(1..n) = product of p^floor(log_p(n)) for all primes p <= n
# log(lcm(1..n)) = sum over primes p<=n of floor(log(n)/log(p))*log(p)
# This is the Chebyshev psi function psi(n)

def log_lcm(n):
    """Compute log(lcm(1..n)) = psi(n) = sum_{p^k <= n} log(p)"""
    if n < 1:
        return 0.0
    result = 0.0
    for p in primerange(2, n+1):
        # add floor(log_p(n)) * log(p)
        pk = p
        lp = math.log(p)
        while pk <= n:
            result += lp
            pk *= p
    return result

# Get primes up to a bound
bound = 10000
primes = list(primerange(2, bound+1))

print(f"Checking inequality for primes up to {bound}")
print(f"Number of primes: {len(primes)}")

violations = []
max_ratio = -1
min_margin = float('inf')

for i in range(len(primes)-1):
    pk = primes[i]
    pk1 = primes[i+1]
    
    # LHS: log(lcm(1..p_{k+1}-1)) = psi(p_{k+1}-1)
    lhs = log_lcm(pk1 - 1)
    
    # RHS: log(p_k * lcm(1..p_k)) = log(p_k) + psi(p_k)
    rhs = math.log(pk) + log_lcm(pk)
    
    margin = rhs - lhs  # should be > 0
    ratio = lhs / rhs
    
    if margin <= 0:
        violations.append((i+1, pk, pk1, lhs, rhs, margin))
        print(f"VIOLATION at k={i+1}: p_k={pk}, p_{{k+1}}={pk1}, LHS={lhs:.6f}, RHS={rhs:.6f}, margin={margin:.6f}")
    
    if margin < min_margin:
        min_margin = margin
        worst_k = i+1
        worst_pk = pk
        worst_pk1 = pk1
    if ratio > max_ratio:
        max_ratio = ratio

print(f"\nTotal violations found: {len(violations)}")
print(f"Minimum margin (RHS-LHS): {min_margin:.6f} at k={worst_k}, p_k={worst_pk}, p_{{k+1}}={worst_pk1}")
print(f"Maximum ratio LHS/RHS: {max_ratio:.8f}")
print(f"\nNote: psi(p_k) = log(lcm(1..p_k))")
print(f"The inequality is equivalent to psi(p_{{k+1}}-1) < log(p_k) + psi(p_k)")
print(f"Since p_{{k+1}}-1 is not prime, psi(p_{{k+1}}-1) = psi(p_k) + contributions from prime powers in (p_k, p_{{k+1}}-1]")
print(f"But (p_k, p_{{k+1}}) contains no primes by definition, so psi(p_{{k+1}}-1) = psi(p_k)")
print(f"Wait - but prime POWERS could be in that range!")

# Let's check: when is psi(p_{k+1}-1) > psi(p_k)?
# Only when there's a prime power p^m with p_k < p^m <= p_{k+1}-1
print("\nCases where psi(p_{k+1}-1) > psi(p_k) (prime power in gap):")
count_extra = 0
for i in range(min(200, len(primes)-1)):
    pk = primes[i]
    pk1 = primes[i+1]
    diff = log_lcm(pk1-1) - log_lcm(pk)
    if diff > 1e-10:
        count_extra += 1
        print(f"  k={i+1}, p_k={pk}, p_{{k+1}}={pk1}, extra psi contribution={diff:.4f}")
print(f"Total such cases in first 200 primes: {count_extra}")