from math import gcd
from functools import reduce

def product_range(a, b):
    """Product of integers from a to b inclusive"""
    result = 1
    for i in range(a, b+1):
        result *= i
    return result

def find_k(n, max_k=200):
    """Find smallest k such that product(n..n+k-1) divides product(n+k..n+2k-1)"""
    for k in range(1, max_k+1):
        p1 = product_range(n, n+k-1)
        p2 = product_range(n+k, n+2k-1)
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
print(f"\nMax k needed: {max(k_values)}")
print(f"Min k needed: {min(k_values)}")

# Check if k=n always works (common conjecture)
print("\nChecking if k=n always works:")
k_equals_n = []
for n in range(1, 51):
    k = n
    p1 = product_range(n, n+k-1)
    p2 = product_range(n+k, n+2*k-1)
    works = (p2 % p1 == 0)
    k_equals_n.append((n, works))
    
print("n, k=n works:")
for n, w in k_equals_n[:20]:
    print(f"  n={n}: {w}")

# Note: product(n+k..n+2k-1)/product(n..n+k-1) = C(n+2k-1, k) * k! / product(n..n+k-1)
# Actually: product(n+k..n+2k-1)/product(n..n+k-1) = C(n+2k-1, k) / C(n+k-1, k) ... let's think differently
# product(n..n+2k-1) = product(n..n+k-1) * product(n+k..n+2k-1)
# So ratio = product(n+k..n+2k-1)/product(n..n+k-1) = C(n+2k-1,k)*k! / (n*(n+1)*...*(n+k-1))
# = (n+2k-1)! / ((n+k-1)! * k!) * k! / ((n+k-1)!/(n-1)!)
# = C(n+2k-1, k) * (n-1)! * k! / ... let me just check numerically

print("\nRatio p2/p1 for k=n, first few n:")
for n in range(1, 11):
    k = n
    p1 = product_range(n, n+k-1)
    p2 = product_range(n+k, n+2*k-1)
    print(f"  n={n}: p2/p1 = {p2//p1} (divisible: {p2%p1==0})")