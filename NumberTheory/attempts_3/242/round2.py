# The previous approach was too slow. Let's optimize significantly.
# Key insight: for each n, we can use algebraic shortcuts.
# Known parametric families that cover most n:
# If n = 4k: 4/n = 1/k (but need 3 terms - use 1/k = 1/(k+1) + 1/(k(k+1)) ... wait need 4/n)
#   4/(4k) = 1/k = 1/(k+1) + 1/(k+1+1) ... no
# 
# Let's use faster approach: for each n, try specific algebraic identities first,
# then fall back to limited search.
#
# Identity 1: if n ≡ 0 mod 4, n=4k: 4/n = 1/k, need to split 1/k into 3 unit fractions
#   1/k = 1/(k+1) + 1/(k(k+1)) -- but that's 2 terms not 3
#   Actually: 4/n directly. Try x = ceil(n/4).
#
# Fast known families:
# 1) n even, n=2m: 4/n = 2/m = 1/m + 1/(m+1) + 1/(m(m+1)) if distinct
# 2) n ≡ 3 mod 4: 4/n = 1/n + 3/n = 1/n + ... 
# 3) General: 4/n = 1/ceil(n/4) + remainder split
#
# Let's implement a fast checker using numpy vectorization over y for each x

import math
import numpy as np

def find_triple_fast(n):
    # Try common parametric forms first (O(1) checks)
    # Form 1: x = (n+1)//4 style
    # 4/n = 1/a + 1/b + 1/c
    
    # Try x = ceil(n/4) to floor(n/2) but limit iterations
    x_min = max(1, (n + 3) // 4)  # ceil(n/4)
    
    # Parametric shortcuts
    # If n is divisible by small numbers, use identities
    # 4/n = 1/n + 1/n + 2/n -- need distinct, so use:
    # 4/n = 1/n + 3/n; 3/n = split
    
    # Fast: for x in small range, vectorize y search
    for x in range(x_min, min(x_min + 200, n)):
        num = 4 * x - n
        den = n * x
        if num <= 0:
            continue
        # y range
        y_min = max(x + 1, -(-den // num))  # ceil(den/num)
        y_max = 2 * den // num
        if y_min > y_max:
            continue
        # vectorized check
        ys = np.arange(y_min, min(y_max + 1, y_min + 50000), dtype=np.int64)
        rem_num = num * ys - den
        mask = rem_num > 0
        ys = ys[mask]
        rem_num = rem_num[mask]
        rem_den = den * ys
        mask2 = rem_den % rem_num == 0
        if mask2.any():
            y = ys[mask2][0]
            z = rem_den[mask2][0] // rem_num[mask2][0]
            if z > y:
                return (x, int(y), int(z))
    return None

# Test correctness
print("Small cases:")
for n in range(3, 21):
    r = find_triple_fast(n)
    print(f"  n={n}: {r}")

# Now test larger range
print("\nTesting n=3 to 100,000:")
failed = []
for n in range(3, 100_001):
    if find_triple_fast(n) is None:
        failed.append(n)

if failed:
    print(f"Failures: {failed[:20]}")
else:
    print("No counterexamples up to 100,000!")