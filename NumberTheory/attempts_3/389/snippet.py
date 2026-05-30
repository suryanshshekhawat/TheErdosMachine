from math import gcd, comb
from sympy import factorint, isprime

def product_range(a, b):
    result = 1
    for i in range(a, b+1):
        result *= i
    return result

# Key insight: divisibility condition is C(n+2k-1,k) / C(n+k-1,k) is integer
# i.e., C(n+k-1,k) divides C(n+2k-1,k)
# 
# For n=1: C(2k,k)/C(k,k) = C(2k,k) - always integer! So k=1 works trivially
# For n=2: need C(k+1,k) | C(2k+1,k), i.e., (k+1) | C(2k+1,k)
# 
# Let's verify: ratio = C(n+2k-1,k)/C(n+k-1,k)
# = product_{i=0}^{k-1} (n+k+i)/(n+i) ... wait let me recompute

# C(n+2k-1,k) = (n+2k-1)!/((n+k-1)! * k!)
# C(n+k-1,k) = (n+k-1)!/((n-1)! * k!)
# ratio = (n+2k-1)! * (n-1)! / ((n+k-1)!)^2 -- same as before

# So we need (n+k-1)!^2 / ((n-1)! * (n+2k-1)! / ... 
# Actually: p1 | p2 iff p2/p1 is integer
# p2/p1 = product_{i=0}^{k-1} (n+k+i)/(n+i)
# = product_{i=0}^{k-1} (n+k+i)/(n+i)

print("Ratio as product:")
for n in range(1, 6):
    for k in range(1, 6):
        ratio_prod = 1
        for i in range(k):
            ratio_prod *= (n+k+i)
        for i in range(k):
            ratio_prod /= (n+i)  # floating point check
        p1 = product_range(n, n+k-1)
        p2 = product_range(n+k, n+2*k-1)
        print(f"  n={n},k={k}: ratio={p2/p1:.4f}, prod_form={ratio_prod:.4f}")

# So divisibility requires: product(n..n+k-1) | product(n+k..n+2k-1)
# which is same as: product_{i=0}^{k-1}(n+i) | product_{i=0}^{k-1}(n+k+i)
# i.e., n*(n+1)*...*(n+k-1) | (n+k)*(n+k+1)*...*(n+2k-1)

# Now n=6 is failing up to k=2000. Let's search much wider
# Use a smarter approach with prime factorizations
def check_divisibility_fast(n, k):
    """Check if product(n..n+k-1) divides product(n+k..n+2k-1)"""
    # Count prime factors in numerator and denominator
    # For each prime p, need v_p(p2) >= v_p(p1)
    p1 = product_range(n, n+k-1)
    p2 = product_range(n+k, n+2*k-1)
    return p2 % p1 == 0

# Search n=6 with larger k
print("\nSearching n=6 up to k=5000:")
found_n6 = False
for k in range(1, 5001):
    if check_divisibility_fast(6, k):
        print(f"  n=6: k={k} works!")
        found_n6 = True
        break
if not found_n6:
    print("  n=6: NOT FOUND up to k=5000")

print("\nSearching n=8 up to k=3000:")
found_n8 = False
for k in range(1, 3001):
    if check_divisibility_fast(8, k):
        print(f"  n=8: k={k} works!")
        found_n8 = True
        break
if not found_n8:
    print("  n=8: NOT FOUND up to k=3000")