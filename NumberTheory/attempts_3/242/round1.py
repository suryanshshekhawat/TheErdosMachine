# Erdős–Straus conjecture: 4/n = 1/x + 1/y + 1/z for distinct integers 1 <= x < y < z
# Let's verify for n from 3 to 10^6 using efficient search

import math

def find_triple(n):
    """Find distinct integers 1 <= x < y < z such that 4/n = 1/x + 1/y + 1/z"""
    # x must satisfy 1/x > 4/(3n) => x < 3n/4
    # also 1/x <= 4/n => x >= n/4
    x_min = max(1, math.ceil(n / 4))
    x_max = math.floor(3 * n / 4)
    
    for x in range(x_min, x_max + 1):
        # remaining: 4/n - 1/x = (4x - n) / (nx)
        num = 4 * x - n
        den = n * x
        if num <= 0:
            continue
        # need 1/y + 1/z = num/den with y < z, y > x
        # y must satisfy: 1/y > num/(2*den) => y < 2*den/num
        # also 1/y <= num/den => y >= den/num
        y_min = max(x + 1, math.ceil(den / num))
        y_max = math.floor(2 * den / num)
        
        for y in range(y_min, y_max + 1):
            # z = 1/(num/den - 1/y) = den*y / (num*y - den)
            rem_num = num * y - den
            if rem_num <= 0:
                continue
            rem_den = den * y
            if rem_den % rem_num == 0:
                z = rem_den // rem_num
                if z > y:
                    return (x, y, z)
    return None

# Test small cases first
print("Testing n=3 to 20:")
for n in range(3, 21):
    result = find_triple(n)
    print(f"  n={n}: {result}")

# Now test up to 10^6
print("\nSearching for counterexamples in n=3 to 1,000,000...")
failed = []
count = 0
for n in range(3, 1_000_001):
    result = find_triple(n)
    if result is None:
        failed.append(n)
    count += 1
    if count % 100000 == 0:
        print(f"  Checked up to n={n}, failures so far: {len(failed)}")

if failed:
    print(f"\nCounterexamples found: {failed[:20]}")
else:
    print(f"\nNo counterexamples found up to n=1,000,000!")
    print("Conjecture holds for all tested n.")