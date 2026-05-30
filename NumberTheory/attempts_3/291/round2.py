from math import gcd, lcm
from sympy import factorint, isprime, primerange

# Analyze the pattern more carefully
# Key observation: gcd=1 cases seem to cluster in specific ranges
# Let's look at the structure of gcd=1 runs

from math import gcd, lcm

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

# Find runs of gcd=1
gcd_one_runs = []
current_run_start = None
for n, a, L, g in results:
    if g == 1:
        if current_run_start is None:
            current_run_start = n
        current_run_end = n
    else:
        if current_run_start is not None:
            gcd_one_runs.append((current_run_start, current_run_end, current_run_end - current_run_start + 1))
        current_run_start = None
if current_run_start is not None:
    gcd_one_runs.append((current_run_start, current_run_end, current_run_end - current_run_start + 1))

print("Runs of consecutive gcd=1 cases:")
for start, end, length in gcd_one_runs:
    print(f"  n={start}..{end}, length={length}")

print()
# Look at where gcd=1 runs START - do they relate to primes/prime powers?
print("Run starts and nearby primes:")
from sympy import nextprime, prevprime
for start, end, length in gcd_one_runs[:20]:
    pp = prevprime(start) if start > 2 else 2
    np_ = nextprime(start)
    print(f"  Run starts at {start}, prevprime={pp}, nextprime={np_}, pp^2={pp**2}")

print()
# Hypothesis: gcd=1 runs occur just after p^2 for prime p?
# Check: after prime squared
primes_sq = [(p, p**2) for p in primerange(2, 100)]
print("Prime squares and whether gcd=1 holds just after:")
for p, p2 in primes_sq:
    if p2 <= 5000:
        # Check n = p2+1, p2+2, ...
        region = [(n, g) for n, a, L, g in results if p2 < n <= p2 + 10]
        print(f"  p={p}, p^2={p2}: next 5 gcds = {[(n,g) for n,g in region[:5]]}")