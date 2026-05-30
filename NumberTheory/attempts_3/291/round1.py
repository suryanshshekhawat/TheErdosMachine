from math import gcd, lcm
from functools import reduce

def compute_sequence(max_n):
    results = []
    
    # We'll track L_n (lcm of 1..n) and a_n (numerator of H_n when written as a_n/L_n)
    # H_n = sum_{k=1}^{n} 1/k = a_n / L_n
    
    current_lcm = 1
    # H_n as fraction: numerator/denominator
    # We'll maintain the sum as an exact fraction
    # sum_num / sum_den = H_n
    # But we want a_n = H_n * L_n
    
    # Better: maintain a_n directly
    # When we go from n to n+1:
    # L_{n+1} = lcm(L_n, n+1)
    # H_{n+1} = H_n + 1/(n+1) = a_n/L_n + 1/(n+1)
    # a_{n+1} = H_{n+1} * L_{n+1}
    #         = (a_n/L_n + 1/(n+1)) * L_{n+1}
    #         = a_n * (L_{n+1}/L_n) + L_{n+1}/(n+1)
    
    L_prev = 1
    a_prev = 1  # H_1 = 1 = 1/1, so a_1 = 1
    
    results.append((1, a_prev, L_prev, gcd(a_prev, L_prev)))
    
    for n in range(2, 5001):
        L_curr = lcm(L_prev, n)
        # a_curr = a_prev * (L_curr // L_prev) + L_curr // n
        a_curr = a_prev * (L_curr // L_prev) + L_curr // n
        
        g = gcd(a_curr, L_curr)
        results.append((n, a_curr, L_curr, g))
        
        L_prev = L_curr
        a_prev = a_curr
    
    return results

results = compute_sequence(5000)

# Analyze gcd values
gcd_1 = [(n, g) for n, a, L, g in results if g == 1]
gcd_gt1 = [(n, g) for n, a, L, g in results if g > 1]

print(f"Total n computed: {len(results)}")
print(f"Cases with gcd=1: {len(gcd_1)}")
print(f"Cases with gcd>1: {len(gcd_gt1)}")
print()
print("First 30 cases with gcd > 1:")
for n, g in gcd_gt1[:30]:
    print(f"  n={n}, gcd={g}")
print()
print("First 30 cases with gcd = 1:")
for n, g in gcd_1[:30]:
    print(f"  n={n}, gcd={g}")
print()

# Check if both cases are frequent
print(f"Fraction with gcd=1: {len(gcd_1)/5000:.4f}")
print(f"Fraction with gcd>1: {len(gcd_gt1)/5000:.4f}")

# Look at gcd values distribution for gcd>1 cases
from collections import Counter
gcd_values = Counter(g for n, g in gcd_gt1)
print("\nGCD value distribution (top 20):")
for val, cnt in sorted(gcd_values.items(), key=lambda x: -x[1])[:20]:
    print(f"  gcd={val}: {cnt} times")