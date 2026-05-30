from math import gcd
from functools import reduce

def product_range(a, b):
    """Product of integers from a to b inclusive"""
    result = 1
    for i in range(a, b+1):
        result *= i
    return result

def find_k(n, max_k=300):
    """Find smallest k such that product(n..n+k-1) divides product(n+k..n+2k-1)"""
    for k in range(1, max_k+1):
        p1 = product_range(n, n+k-1)
        p2 = product_range(n+k, n+2*k-1)
        if p2 % p1 == 0:
            return k
    return None

# Check for n from 1 to 200
results = {}
failed = []
for n in range(1, 201):
    k = find_k(n, max_k=300)
    if k is None:
        failed.append(n)
    else:
        results[n] = k

print(f"Checked n=1 to 200 with max_k=300")
print(f"Failed (no k found): {failed}")
print(f"\nFirst 30 results (n: k):")
for n in range(1, 31):
    if n in results:
        print(f"  n={n}: k={results[n]}")

# Look at pattern of k values
k_values = [results[n] for n in range(1, 201) if n in results]
if k_values:
    print(f"\nMax k needed: {max(k_values)}")
    print(f"Min k needed: {min(k_values)}")

# Check if k=n always works (common conjecture)
print("\nChecking if k=n always works:")
for n in range(1, 31):
    k = n
    p1 = product_range(n, n+k-1)
    p2 = product_range(n+k, n+2*k-1)
    works = (p2 % p1 == 0)
    print(f"  n={n}, k={n}: works={works}, ratio={p2//p1 if works else 'N/A'}")

# The ratio product(n+k..n+2k-1)/product(n..n+k-1) when k=n:
# = product(2n..3n-1)/product(n..2n-1)
# = C(3n-1, n) * n! / product(n..2n-1) ... let's compute directly
print("\nFor k=n: ratio = product(2n..3n-1)/product(n..2n-1)")
print("This equals C(3n-1,n)/C(2n-1,n) * something... let's just see values")
for n in range(1, 20):
    k = n
    p1 = product_range(n, n+k-1)   # product(n..2n-1)
    p2 = product_range(n+k, n+2*k-1) # product(2n..3n-1)
    ratio = p2 / p1
    print(f"  n={n}: ratio={ratio:.4f}")