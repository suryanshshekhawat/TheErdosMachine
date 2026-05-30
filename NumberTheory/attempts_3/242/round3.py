# No numpy available. Use pure Python with optimized math.
# Key: use fast parametric identities to cover most n, minimal fallback search.

import math

def find_triple(n):
    # Parametric families that cover most cases:
    
    # Family 1: if n % 4 == 0, n=4k
    # 4/(4k) = 1/k = 1/(k+1) + 1/(k+1) -- not distinct
    # Better: 4/n = 1/(n//4) but split differently
    # 4/n = 1/a + 1/b + 1/c
    
    # Try: 4/n = 1/n + 1/n + 2/n -- not distinct
    # Use: if n even, n=2m: 4/n=2/m
    #   2/m = 1/m + 1/m -- not distinct, so
    #   try 4/n = 1/(n/2) + 1/(n/2+1) + 1/(n/2*(n/2+1)) * ... check
    
    # Most efficient known: for each n, try x = ceil(n/4), ceil(n/4)+1, ...
    # For given x, compute y,z algebraically in O(1) if divisibility holds
    # Also try x = n//3, x = n//2, etc.
    
    # Approach: limit x to ~sqrt(n) range from ceil(n/4)
    x_min = (n + 3) // 4  # ceil(n/4)
    
    # Also try some specific x values known to work for many n
    # x = (n+1)//4, n//3, n//2, n, etc.
    
    x_limit = x_min + 3 * int(math.isqrt(n)) + 100
    
    for x in range(x_min, x_limit + 1):
        num = 4 * x - n   # = 4x - n
        den = n * x       # numerator of remainder after subtracting 1/x
        if num <= 0:
            continue
        # need 1/y + 1/z = num/den, y > x, z > y
        # y_min = ceil(den/num), y_max = floor(2*den/num)
        y_min = max(x + 1, (den + num - 1) // num)  # ceil(den/num)
        y_max = (2 * den) // num
        
        if y_min > y_max:
            continue
        
        # For each y, z = den*y/(num*y - den); check if integer and z > y
        for y in range(y_min, y_max + 1):
            rem = num * y - den
            if rem <= 0:
                continue
            if (den * y) % rem == 0:
                z = (den * y) // rem
                if z > y:
                    return (x, y, z)
    return None

# Verify small cases
print("Small cases n=3..30:")
for n in range(3, 31):
    r = find_triple(n)
    print(f"  n={n}: {r}")

# Test up to 100k, track time and failures
import time
start = time.time()
failed = []
checked = 0
for n in range(3, 100_001):
    r = find_triple(n)
    if r is None:
        failed.append(n)
    checked += 1
    if checked % 10000 == 0:
        elapsed = time.time() - start
        print(f"  Checked {checked}, time={elapsed:.1f}s, failures={len(failed)}")
        if elapsed > 40:
            print(f"  Stopping early at n={n}")
            break

print(f"\nChecked {checked} values in {time.time()-start:.1f}s")
if failed:
    print(f"FAILURES: {failed}")
else:
    print(f"No counterexamples found up to n={2+checked}!")