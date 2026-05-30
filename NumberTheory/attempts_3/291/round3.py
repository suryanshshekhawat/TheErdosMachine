from math import gcd, lcm, isqrt

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

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0: return False
    return True

results = compute_sequence(5000)

# Find runs of gcd=1
gcd_one_runs = []
current_run_start = None
current_run_end = None
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

print("Runs of consecutive gcd=1 cases (start, end, length):")
for start, end, length in gcd_one_runs:
    print(f"  n={start}..{end}, length={length}")

print()
# Check if run starts relate to prime squares
print("Checking relation to prime squares:")
primes = [p for p in range(2, 200) if is_prime(p)]
prime_squares = {p: p*p for p in primes if p*p <= 5000}

for start, end, length in gcd_one_runs:
    # Find nearest prime square <= start
    nearby = [(p, p2) for p, p2 in prime_squares.items() if p2 <= start + 5]
    if nearby:
        best = max(nearby, key=lambda x: x[1])
        p, p2 = best
        print(f"  Run [{start}..{end}] len={length}: prev prime sq = {p}^2={p2}, diff={start-p2}")

print()
# Look at what prime divides gcd just before each run
print("GCD just before each gcd=1 run:")
gcd_dict = {n: g for n, a, L, g in results}
for start, end, length in gcd_one_runs[:15]:
    if start > 1:
        g_before = gcd_dict[start - 1]
        g_after_end = gcd_dict.get(end + 1, None)
        print(f"  Run [{start}..{end}]: gcd[{start-1}]={g_before}, gcd[{end+1}]={g_after_end}")