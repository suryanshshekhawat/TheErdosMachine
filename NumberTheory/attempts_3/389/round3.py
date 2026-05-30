from math import gcd
from functools import reduce

def product_range(a, b):
    """Product of integers from a to b inclusive"""
    result = 1
    for i in range(a, b+1):
        result *= i
    return result

# The search with max_k=300 seems to have missed valid k for n>=6
# Let's try much larger max_k for small n values
# Also re-examine: for n=4, k=207 and n=5, k=206 were found
# But n=6 through 200 failed with max_k=300 - need larger search

# First, verify n=4, k=207 and n=5, k=206
for n, k in [(4, 207), (5, 206)]:
    p1 = product_range(n, n+k-1)
    p2 = product_range(n+k, n+2*k-1)
    print(f"n={n}, k={k}: divisible={p2 % p1 == 0}")

# Now try larger max_k for n=6,7,8
print("\nSearching larger k for n=6,7,8,9,10:")
for n in range(6, 11):
    found = False
    for k in range(1, 2000):
        p1 = product_range(n, n+k-1)
        p2 = product_range(n+k, n+2*k-1)
        if p2 % p1 == 0:
            print(f"  n={n}: k={k}")
            found = True
            break
    if not found:
        print(f"  n={n}: NOT FOUND up to k=2000")

# Key observation: ratio = product(n+k..n+2k-1)/product(n..n+k-1)
# = (n+2k-1)! / ((n+k-1)! * k!) * (k! * (n-1)!) / (n+k-1)! * (n+k-1)!/(n-1)!
# Actually: ratio = C(n+2k-1, k) / C(n+k-1, k) * ... 
# Let me think more carefully:
# product(n+k..n+2k-1) = (n+2k-1)!/(n+k-1)!
# product(n..n+k-1) = (n+k-1)!/(n-1)!
# ratio = (n+2k-1)! * (n-1)! / ((n+k-1)!)^2
# = C(n+2k-1, k) * k! * (n-1)! / (n+k-1)!
# = C(n+2k-1, k) / C(n+k-1, k)

print("\nRatio formula: product(n+k..n+2k-1)/product(n..n+k-1) = C(n+2k-1,k)/C(n+k-1,k)")
print("Verifying:")
from math import comb
for n in range(1, 6):
    for k in range(1, 6):
        p1 = product_range(n, n+k-1)
        p2 = product_range(n+k, n+2*k-1)
        ratio_direct = p2 / p1
        ratio_formula = comb(n+2*k-1, k) / comb(n+k-1, k)
        print(f"  n={n},k={k}: direct={ratio_direct:.4f}, formula={ratio_formula:.4f}, match={abs(ratio_direct-ratio_formula)<1e-9}")