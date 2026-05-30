from math import gcd, log
from sympy import primerange, nextprime

def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_range(n):
    result = 1
    for i in range(2, n+1):
        result = lcm(result, i)
    return result

# Instead of computing huge numbers directly, work in log space
# log(lcm(1..n)) = sum of log(p^floor(log_p(n))) for primes p <= n
# This equals sum over primes p <= n of floor(log(n)/log(p)) * log(p)

import math

def log_lcm(n):
    """Compute log(lcm(1,...,n)) exactly using prime factorization."""
    result = 0.0
    for p in primerange(2, n+1):
        # Highest power of p <= n
        pk = p
        while pk <= n:
            result += math.log(p)
            pk *= p
    return result

# Verify: log(lcm(1..p_{k+1}-1)) < log(p_k) + log(lcm(1..p_k))
# i.e., log_lcm(p_{k+1}-1) < log(p_k) + log_lcm(p_k)

primes = list(primerange(2, 10000))

violations = []
results = []

for k in range(len(primes)-1):
    pk = primes[k]
    pk1 = primes[k+1]
    
    lhs = log_lcm(pk1 - 1)
    rhs = math.log(pk) + log_lcm(pk)
    
    diff = rhs - lhs
    results.append((k+1, pk, pk1, lhs, rhs, diff))
    
    if lhs >= rhs:
        violations.append((k+1, pk, pk1, lhs, rhs, diff))

print(f"Checked k=1 to k={len(primes)-1}, primes up to p_k={primes[-2]}, p_{{k+1}}={primes[-1]}")
print(f"Total violations found: {len(violations)}")

if violations:
    print("VIOLATIONS:")
    for v in violations:
        print(f"  k={v[0]}, p_k={v[1]}, p_{{k+1}}={v[2]}, lhs={v[3]:.6f}, rhs={v[4]:.6f}, diff={v[5]:.6f}")
else:
    print("No violations found!")

# Show first few and some statistics
print("\nFirst 10 cases:")
for r in results[:10]:
    print(f"  k={r[0]}, p_k={r[1]}, p_{{k+1}}={r[2]}, lhs={r[3]:.4f}, rhs={r[4]:.4f}, margin={r[5]:.4f}")

# Check minimum margin
min_margin = min(r[5] for r in results)
min_case = min(results, key=lambda r: r[5])
print(f"\nMinimum margin: {min_margin:.6f} at k={min_case[0]}, p_k={min_case[1]}, p_{{k+1}}={min_case[2]}")

# The inequality is equivalent to: lcm(1..p_{k+1}-1) / lcm(1..p_k) < p_k
# Note: lcm(1..m)/lcm(1..m-1) = m if m is a prime power, else 1
# So lcm(1..p_{k+1}-1)/lcm(1..p_k) = product of prime powers p^a where p_k < p^a < p_{k+1}
print("\nAnalysis of ratio lcm(1..p_{k+1}-1)/lcm(1..p_k):")
print("(This ratio = product of prime powers strictly between p_k and p_{k+1})")
for k_idx in range(min(20, len(primes)-1)):
    pk = primes[k_idx]
    pk1 = primes[k_idx+1]
    # prime powers strictly between pk and pk1
    prime_powers_between = []
    for p in primerange(2, pk1):
        pp = p
        while pp <= pk1 - 1:
            if pp > pk:
                prime_powers_between.append(pp)
            pp *= p
    log_ratio = sum(math.log(pp) for pp in prime_powers_between)
    print(f"  k={k_idx+1}, [{pk},{pk1}]: prime powers between = {prime_powers_between}, log_ratio={log_ratio:.4f}, log(p_k)={math.log(pk):.4f}")